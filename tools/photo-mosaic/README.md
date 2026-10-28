# Native-resolution photo mosaic

Offline Python tools for overlapping photographs of one mostly planar surface. Original files remain unchanged. Feature matching and sparse global refinement establish geometry; tiled lossless TIFF/BigTIFF rendering retains the finest estimated source sampling without super-resolution or generated detail.

Tall components, changing viewpoints, reflections and missing coverage can prevent a uniformly sharp composite. Focus selection cannot recover detail absent from every source image or resolve incorrect geometry. Small residuals are not calibrated dimensional accuracy.

## Environment

Linux and Python 3.12 are the tested platform. Required libraries are NumPy, OpenCV, SciPy, Pillow, tifffile, imagecodecs and threadpoolctl. The [environment specification](environment.yml) pins the versions used in the project-local environment. A fresh installation from that specification has not been verified; package availability and native-library dependencies remain environment-dependent. No runtime, model weights or dependency payloads are bundled.

With an existing conda-compatible package manager, a project-local environment can be created with:

```bash
conda env create --prefix .venv/photo-mosaic --file tools/photo-mosaic/environment.yml
conda activate ./.venv/photo-mosaic
```

Commands below run from the repository root with those dependencies available. Installation requires registry access and disk space. The scripts do not install system packages or manage the package manager's external cache configuration.

## Intake and registration

`ARCHIVE_PATH` and `SOURCE_DIRECTORY` below are placeholders for an authorized input archive and the extracted image directory.

```bash
python tools/photo-mosaic/import_tar.py ARCHIVE_PATH --destination tools/photo-mosaic/inbox/board
python tools/photo-mosaic/assess_inputs.py tools/photo-mosaic/inbox/board/raw --output tools/photo-mosaic/inbox/board/quality.json
python tools/photo-mosaic/mosaic.py build SOURCE_DIRECTORY --run board --preview-only
```

TAR intake records original byte hashes, resumes by verifying existing files and rejects traversal, links, special entries and conflicting originals. ZIP/directory intake is also available through `mosaic.py import --help`. A `.partial` file is an incomplete local copy, not an original.

Registration byte-deduplicates readable sources, caches SIFT features and pair matches, requires connected overlap coverage and rejects unstable or inconsistent transforms. Bounded workers limit concurrent decoding and matching. Default worker counts are four for features and six for pairs, controlled by `PHOTO_MOSAIC_FEATURE_WORKERS` and `PHOTO_MOSAIC_WORKERS` respectively. Feature workers use one OpenCV thread each.

`--resume` with identical build arguments reuses completed caches. Changed inputs or options require a new run name. Quality scores and perceptual hashes are scene-dependent indicators; matching perceptual hashes alone never authorize deleting originals.

## PCB surface matching

A green PCB photographed beside a movable case or another background plane can produce convincing but incorrect overlaps. The optional `mask_pcb_cached.py --parent RUN --run MASKED_RUN` step constrains registration to the largest green board region and nearby silkscreen. Correspondences already inside both masks are reused; other candidate pairs are matched again with filtered descriptors. Original photographs remain unchanged and native rendering still uses the complete source pixels.

This mask is specific to green PCB imagery. It is not a general subject detector: unrelated green objects, unusual lighting, other board colours or tiny visible board regions require inspection. `masks/` previews and graph connectivity must be checked before refinement. No disconnected component is silently discarded.

## Projective refinement and rendering

For perspective variation, a completed pair cache and connected graph can be refined separately. An affine consistency failure can leave usable measurements; it does not justify ignoring the geometric error guard.

```bash
python tools/photo-mosaic/refine_cached.py --parent tools/photo-mosaic/runs/board --run tools/photo-mosaic/runs/board-projective
python tools/photo-mosaic/render_alignment.py --parent tools/photo-mosaic/runs/board --alignment-run tools/photo-mosaic/runs/board-projective --output tools/photo-mosaic/runs/board-result --preview --blend focus
```

`preview-fast.png`, coverage and alignment residuals require inspection before native rendering. Solver evaluation limits are recorded; an evaluation limit is not reported as mathematical convergence. Out-of-bound measured edges cause failure. Frame reflections, extreme transforms, false repetitive matches and component parallax require investigation rather than blind retries.

If inspection establishes unreliable overlap edges, `prune_refinement.py --parent RUN --initial-run REFINED_RUN --run NEW_RUN` records and rejects edges whose saved global median error exceeds the existing threshold. A disconnected result is rejected without dropping source images. Re-fitting must pass the unchanged geometric guard before an accepted alignment is exported. The rejection log is evidence for review, not proof that every retained correspondence is correct.

The same render command without `--preview` writes the native result. An optional `--geometry` argument accepts a reviewed project-relative JSON file containing `width`, `height` and one native transform per source; this is an advanced interface for verified cropping, not an automatic gap-repair mechanism.

## Focus, output and resume

- `focus` selects the locally stronger multiscale contrast from aligned native sources rather than averaging sharp and defocused pixels. Hard source transitions can remain. It is a focus-fusion method, not an optical-sharpness guarantee.
- `feather` averages overlaps with edge, clarity and highlight weights. `best` selects the largest feather/clarity weight rather than local focus.
- Disk-backed buffers and stripe warps bound render memory. Output size and free-space checks remain necessary. Generated TIFFs are losslessly compressed and accompanied by a separate coverage mask; uncovered regions are reported rather than invented.
- The focus cache retains a content/geometry identity and periodic checkpoints. Replaying an unfinished chunk uses idempotent maximum selection. Orderly process interruption and cached re-export are tested; arbitrary storage corruption or power-loss durability is not guaranteed.
- `render-progress.json` and quality reports describe progress. Native output is published by atomic filename replacement after export. Resume never silently accepts changed source identities.
- Exports omit identifying EXIF/XMP/IPTC. Structural TIFF fields and generic software tags may remain. Identifying pixels still require separate review and opaque redaction before sharing.

Images, feature caches, intermediate buffers and generated reports are excluded from this repository. Optional PNG/JPEG copies require separate export and metadata checks; no output is assumed complete until decoded and inspected.

## Raised components and final composition

Global board-plane alignment can fragment capacitors, connectors and chip surfaces when viewpoints change. The optional `refine_patch.py` helper ranks full-coverage native source regions and permits bounded local ECC alignment. `--reference-only` saves one coherent source view without stacking. Without that option, the helper invokes a separately installed `focus-stack` executable; `--focus-stack` accepts an explicit executable path. No external binary is bundled or downloaded. The private project launcher is used only when present locally.

The `--roi` coordinates are numeric x/y/width/height on the union preview whose longest side is 2,048 pixels. Regional output remains on the native mosaic grid. Stack outputs require visual inspection: combining different surfaces or viewpoints can introduce artifacts even after local alignment. A reviewed single-source region can be preferable to an inconsistent stack.

`compose_regions.py SPEC_JSON` blends reviewed native regions using explicit polygons, optionally trims/rotates the composite and removes outside-subject background. The specification contains a base TIFF, native crop coordinates, region files/metadata, normalized region polygons, output directory and optional foreground polygons. `--preview-only` allows inspection before export. This advanced helper currently requires 8-bit RGB; other depths fail explicitly. It writes lossless RGB BigTIFF, RGBA PNG with transparent outside-subject pixels, a subject mask and JPEG preview. Images and dataset-specific specifications remain untracked.

Regional composition preserves source white balance. A per-channel normalization trial produced visible casts and was rejected. Tests check RGB channel order, unchanged pixels outside selected patches, lossless TIFF/PNG agreement, trim/rotation and foreground alpha. No inpainting or generated detail is used. Uneven source sharpness and small residual perspective, seam or reflection errors can remain.

## Tests

```bash
python -m unittest discover -s tools/photo-mosaic/tests -v
```

Synthetic tests cover affine/projective registration, 16-bit TIFFs, coverage, original preservation, identity guards, disconnected inputs, focus selection, interrupted/cached rendering safe archive intake and rejection of a separate green connector/background in a synthetic PCB mask. Real-dataset sharpness requires additional visual checks; synthetic success is not proof of every composite's quality.

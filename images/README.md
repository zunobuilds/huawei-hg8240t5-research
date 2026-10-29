# Image provenance

This repository includes an exterior view, two PCB backside details and composites of both board surfaces. The flat-side composite has separate preview and full-resolution files. Originals remain unchanged. EXIF/XMP/IPTC and other removable metadata were stripped from the included copies.

| File | Contents | Limitation |
| --- | --- | --- |
| [Flat-side composite](pcb/pcb-flat-side.jpg), [full resolution](pcb/pcb-flat-side-full.jpg) | Top-facing PCB surface, 14,216 × 8,923 native pixels; 3,200-pixel preview | Serial/QR sticker covered; source blur and alignment limits remain |
| [Component-side composite](pcb/pcb-component-side.jpg) | Bottom-facing PCB side with connectors and components | Reduced multi-view composite; source blur, seams and parallax can remain |
| [Exterior view](device/hg8240t5-exterior.jpg) | Enclosure, vented top and Singtel branding | Cropped and colour-adjusted photograph; perspective and depth of field limit measurements |
| [Connector region](pcb/pcb-connector-side.jpg) | Connector housings, solder joints and backside components | Partial board view; glare |
| [Trace detail](pcb/pcb-trace-detail.jpg) | Backside traces, solder joints and footprints | Soft focus limits fine marking interpretation |

I selected the exterior image from the enclosure photo set and used GIMP to crop it and adjust its tone and colour. It is a 1,800 × 1,128 pixel export from the camera JPEG, with no generative editing or reconstructed detail.

I selected the PCB detail frames to exclude the board's identifying serial/QR sticker. The two PCB copies retain the original JPEG encoded image data and capture orientation. No sharpening, component reconstruction or signal annotation was applied.

Public file hashes are in [SHA256SUMS](SHA256SUMS). Unredacted masters, raw frame collections and identifying overviews are excluded. Component identifications rely on the broader private research, not these photographs alone.

The small [AI-assisted label](ai-assisted.svg) beneath the README title is project-created SVG text artwork. It discloses AI assistance; it is not a device photograph, certification or external service badge.

I produced the component-side image from 1,297 photographs using guarded projective registration, local focus selection and reviewed regional composition. The lossless master remains local. No AI-generated detail, inpainting or arbitrary post-render enlargement was applied.

The flat-side exports come from the existing GIMP-redacted lossless master assembled from 694 photographs. The sticker is covered in the source raster. The full-resolution JPEG retains native dimensions; the preview is downsampled. Both were exported without EXIF, embedded thumbnails or identifying metadata. Original photographs and TIFF masters remain unchanged.

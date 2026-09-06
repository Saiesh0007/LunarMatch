# LunarMatch — Data + Preprocessing Engineer Design

## Goal

Image ingestion, validation, normalization, illumination-aware preprocessing, scale/resolution preparation

## Files Owned

- `src/io.py`
- `src/preprocessing.py`

## Interface

```python
load_image(path) -> image, metadata

preprocess(
    image,
    sensor,
    config
) -> {
    "image": processed_image,
    "metadata": metadata,
    "scale_factor": scale_factor
}
```

## Preprocessing Chain

Start with:
1. grayscale where appropriate
2. normalization
3. denoising
4. CLAHE/local contrast enhancement
5. optional illumination normalization

## Scale Handling

Provide a clear working-scale factor so downstream modules can relate working coordinates to original coordinates.

## Validation

Reject:
- unreadable files
- empty images
- unsupported dimensions
- invalid pixel ranges

## Deliverable

A preprocessing module that can process the known-good test pairs consistently.

## Visual Priority

```text
Registered result
>
Correspondence visualization
>
Metrics
>
Pipeline status
>
Configuration
```

## Demo Requirement

A panel member should understand the result without reading source code.

## Failure Requirement

The system should explain when a registration is unreliable.

# LunarMatch — Tech Lead + Integration Design

## Goal

System orchestration, interfaces, end-to-end pipeline, Git/GitHub integration, final reliability

## Files Owned

- `src/pipeline.py`
- `src/config.py`
- integration tests
- repository structure
- CI/basic test runner if time permits

## Primary Interface

```python
run_lunarmatch(
    reference,
    moving,
    reference_sensor,
    moving_sensor,
    config
)
```

## Expected Result

```python
{
    "status": "success",
    "registered_image": ...,
    "matches": ...,
    "inliers": ...,
    "transformation": ...,
    "metrics": ...
}
```

## Integration Duties

- define interfaces before parallel work starts
- maintain `develop`
- merge pull requests
- resolve interface conflicts
- run end-to-end tests
- maintain primary and backup demo pairs

## Do Not Own

Do not become the sole implementer of every algorithm. Your job is integration and reliability.

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

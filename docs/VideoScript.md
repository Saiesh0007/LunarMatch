# LunarMatch — YouTube Video Script

**Length:** about 11 minutes. PPT about 5.5 min, mobile app about 3.5 min, website about 2 min.

How to read this:
- **[SCREEN]** is what to show or click. Don't read it out.
- Plain text is what you say. It's written to be read aloud at a calm pace (about 140 words a minute).
- *(pause)* means stop for a beat so the viewer can see the screen.
- The numbers in the app and the website come from the run. **Read them off the screen**. The numbers here are what we usually get.

---

## Before you hit record

- [ ] Backend running: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Web app running (`cd web && npm run dev`) or the live site open: https://spectrum-gules.vercel.app/
- [ ] Web header shows **FASTAPI: ONLINE** (not FLIGHT SIMULATION)
- [ ] `backend/data/real/pairs/ch2_tmc_iirs_3/ref_iirs.png` and `mov_tmc2.png` open in a file explorer, ready to drag
- [ ] Two unrelated images ready (for the fail-safe demo)
- [ ] Mobile app running (`flutter run -d windows` or emulator). Home screen shows backend online
- [ ] PPT in slideshow mode, notifications off, browser zoom set to 100 %
- [ ] Do one practice run of the Studio, so the backend is warm and the real take is fast

---

# PART 1 — PRESENTATION (0:00 – 5:30)

### Slide 1 — Title (0:00 – 0:30)

**[SCREEN]** Title slide: SIH 2026, PS 26166, Team ID 127530, Team Spectrum.

Hello everyone, we are **Team Spectrum**, team ID 127530, for Smart India Hackathon 2026.

Our problem statement is **26166**, under the Space Technology theme: *multi-modal, sun-angle and scale-invariant image correspondence using Chandrayaan-2 optical images from OHRC, TMC and IIRS.*

Our solution is called **LunarMatch**. We'll walk through the idea in six slides and then show the working mobile app and website.

---

### Slide 2 — Idea Title: Problem, Solution, Uniqueness (0:30 – 1:45)

**[SCREEN]** Slide 2. Start on the left, **THE PROBLEM**, with its four challenges.

On the left is **the problem**. Matching lunar images from Chandrayaan-2 is hard for four reasons:

- **Different sensors.** OHRC, TMC-2 and IIRS see the same ground very differently. One is a high-resolution camera, and IIRS is an infrared spectrometer with 256 bands.
- **Different sun angles.** Shadows inside craters move, shrink or flip between passes.
- **Different scales.** The resolutions range from about 25 centimetres to about 80 metres per pixel.
- **Different viewpoints**, which bring geometric distortion.

**[SCREEN]** Move to the centre, **OUR SOLUTION — LunarMatch Engine**.

**Our solution is the LunarMatch engine.** Input data goes through a chain of stages: illumination-aware preprocessing, resolution alignment, robust features using RIFT2 and SuperPoint, learned matching with LightGlue and SuperGlue, spatially balanced correspondences, robust estimation with MAGSAC++, and finally sub-pixel refinement.

**[SCREEN]** Move to the right, **UNIQUENESS**.

What makes it **unique**:
- one unified pipeline across OHRC, TMC and IIRS
- robust to sun angle and scale changes
- works across sensors and resolutions
- spreads match points uniformly across the image, not just on crater rims
- registers with sub-pixel accuracy
- scales to more sensors and data

In one line: *LunarMatch, towards a unified view of the Moon.*

---

### Slide 3 — Technical Approach (1:45 – 3:10)

**[SCREEN]** Slide 3. Follow the numbered boxes 01 → 05.

Our technical approach runs in five stages.

**01, data sources.** Chandrayaan-2 OHRC for high resolution, TMC-2 for medium and IIRS for low resolution, with LRO NAC and SELENE as reference imagery. We read the raw ISRO PDS4 products directly, including the labels with resolution, sun angles and footprint.

**02, data standardisation.** Radiometric and contrast normalisation, resolution and scale normalisation, and geometric preprocessing such as denoising and cropping. You can see the before and after here: the images become consistent enough to extract features from.

**03, robust representation.** We use phase-congruency features based on RIFT2, which respond to structure rather than brightness, together with structural HOPC descriptors and a multi-scale pyramid. For the hardest cross-sensor pairs we also have a dense structural matcher, CFOG, that takes over automatically when sparse features fail.

**04, correspondence and geometry.** Matches go through optimal-transport matching, using log-domain Sinkhorn with dustbin handling for unmatched points. They are then spatially balanced for uniform distribution and verified with MAGSAC++.

**05, refinement and decision.** We estimate an affine or homography transform, refine it with sub-pixel phase correlation, and compute explainable quality metrics. The result is **ACCEPTED**, or **REJECTED with the reason**.

**[SCREEN]** Point to the tech stack and links at the bottom.

The tech stack is Python, OpenCV, NumPy and SciPy on the backend and TypeScript on the web. The GitHub repo, the deployed website, the APK and this video are all linked here.

---

### Slide 4 — Feasibility and Viability (3:10 – 4:10)

**[SCREEN]** Slide 4. Start with **FEASIBILITY ANALYSIS**: four boxes.

Is it feasible? Yes, on four counts.
- **Technical:** every component exists, is mature, and integrates well.
- **Data:** Chandrayaan-2, LRO and SELENE datasets are publicly available.
- **Infrastructure:** it runs on an ordinary CPU, and it can also be deployed in the cloud.
- **Scalability:** the pipeline is modular, so it's easy to extend and reuse.

And it isn't just on paper. We tested it on **real Chandrayaan-2 data**: six TMC-2 and IIRS pairs from the same orbit across 900 km of strip. **All six registered**, in about seven seconds each, with a median error of about 1.4 IIRS pixels.

**[SCREEN]** Move to **RISK MITIGATION**: read each risk with its fix.

For each risk we have a mitigation:
- **Large illumination differences** → illumination-aware preprocessing and RIFT features.
- **Cross-sensor appearance variation** → multimodal feature benchmarking, plus the dense structural fallback.
- **Scale variation** → resolution alignment and scale-robust features.
- **False correspondences** → robust estimation with MAGSAC++.
- **Uneven spatial distribution** → spatially balanced match selection.
- **The sub-pixel requirement** → local geometric refinement.

---

### Slide 5 — Impact and Benefits (4:10 – 4:55)

**[SCREEN]** Slide 5. Point to the **Evaluation Parameters** first.

Every result is judged on four **evaluation parameters**: **RMSE**, **inlier ratio**, **inlier count** and **spatial coverage**. These are computed from each actual run, not hard-coded.

**[SCREEN]** Follow the flow in the centre, then the **Key Benefits**.

The flow goes from multi-sensor lunar data, to reliable matching, to high-precision registration, to scientifically aligned data.

The **key benefits**:
- **Scientific analysis**: studying terrain, geology and resources across sensors.
- **Mission support**: better navigation, planning and decisions.
- **Map mosaicing**: seamless lunar maps from multiple sensors.
- **Change detection**: comparing the same ground across times, lighting and sensors.

---

### Slide 6 — Research and References (4:55 – 5:30)

**[SCREEN]** Slide 6. Point to **Existing Approaches**, then **Research Gap**.

Existing approaches fall into two groups. **Classical methods** are SIFT, ASIFT, AKAZE and RIFT. **Learned methods** are SuperPoint, SuperGlue and LightGlue.

The **research gap** is that each of these solves only part of the problem. LunarMatch brings it together in one pipeline that handles multimodal data, sun angle, scale, spatial coverage, robust geometry and sub-pixel accuracy.

**[SCREEN]** Point to the dataset and reference links.

Our data comes from ISRO's ISSDC Chandrayaan-2 browser and the LROC QuickMap. Our references and full literature review are linked here.

Now let's see it working, starting with the mobile app.

---

# PART 2 — MOBILE APP (5:30 – 9:00)

### Home (5:15 – 5:35)

**[SCREEN]** Switch to the app. Splash animation, then Home. Point at the backend status.

This is the LunarMatch mobile app, built in Flutter. It runs on Android, Windows and the web.

On the home screen you can see the backend status. It's online, so everything we run here is processed live by our engine. There are four entry points: image registration, the robustness lab, pipeline architecture and engine capabilities.

### Select images (5:35 – 6:00)

**[SCREEN]** Tap **Image Registration**. Pick a demo pair. Tap **SWAP REFERENCE & MOVING** once, then swap back.

First we pick the images. The **reference** image is the fixed frame, and the **moving** image is the one we transform onto it. I'm using one of the bundled demo pairs. These are synthetic prototypes, and we label them that way. You can also upload your own images. The swap button flips the roles.

### Configure (6:00 – 6:40)

**[SCREEN]** Configuration screen. Scroll slowly through each section.

Now the pipeline configuration.

**Feature method:** RIFT2 is the default. We also have SIFT and SuperPoint.
**Matcher:** brute force, FLANN, or the learned SuperGlue and LightGlue.
**Geometric model:** homography or affine.
And **spatial grid partitioning**, plus preprocessing options like CLAHE contrast enhancement and edge-preserving denoising.

I'll keep RIFT2 and run it.

### Execution (6:40 – 7:00)

**[SCREEN]** Pipeline execution screen with the stages ticking through.

You can see the pipeline running through its ten stages, each with its own timing, from ingestion through feature extraction, matching, MAGSAC++ and refinement.

### Result (7:00 – 7:50)

**[SCREEN]** Result screen. Show the banner, then toggle REF / REGISTERED / OVERLAY / DIFF, then scroll to the metrics and the matrix.

Here's the result. At the top is the decision banner: *(read it, e.g. "successful, high confidence")*.

We can compare the views: the reference, the registered image, an overlay, and the difference map. *(toggle each one)* In the difference map, a good registration leaves very little structure behind.

Below are the measured metrics: *(read off the screen)* number of inliers, inlier ratio, spatial coverage and RMSE in pixels. Then the sub-pixel refinement statistics and the actual transformation matrix. You can export the whole thing as a report.

### Spatial grid and pipeline details (7:50 – 8:15)

**[SCREEN]** Open **Spatial coverage**, then **Pipeline details**.

The spatial coverage screen shows grid occupancy before and after balancing. This is how we make sure matches are spread across the image, not just clustered on crater rims.

Pipeline details shows the real stage timeline returned by the backend for this run.

### Robustness lab and capabilities (8:15 – 8:45)

**[SCREEN]** Go to **Robustness laboratory**, run an illumination sweep. Then open **Engine capabilities**.

In the robustness lab we can stress-test the engine. Here's an illumination sweep: the same image registered against versions with changed brightness. For every step we get inliers, ratio, coverage, RMSE and a pass or fail.

And engine capabilities lists everything the backend supports, served live by the API.

The app also has an offline mode that replays bundled demo results, so it can be demonstrated without a network.

Now let's look at the website, where we'll use real Chandrayaan-2 data.

---

# PART 3 — WEBSITE (9:00 – 11:00)

### Overview (8:45 – 9:00)

**[SCREEN]** Browser on the **Overview** tab. Point at **FASTAPI: ONLINE** in the header.

This is the LunarMatch web app. The header shows the backend is online. The overview lists the supported sensors: OHRC, TMC-2, IIRS, LRO NAC and SELENE.

### Studio: real Chandrayaan-2 run (9:00 – 9:55)

**[SCREEN]** Click **Studio**. Drag `ref_iirs.png` into **REF (FIXED)** and `mov_tmc2.png` into **MOVING**.

In the Studio I'm loading **genuine Chandrayaan-2 data from the same orbit**: an IIRS infrared image as the reference and a TMC-2 camera image as the moving image. They come from two completely different instruments, with a four-times resolution gap.

**[SCREEN]** Descriptor pipeline: **Dense Structural CFOG**. Metadata: REF **IIRS / 78.32**, MOV **TMC-2 / 19.6**. Click **EXECUTE REGISTRATION ENGINE**.

I'll choose the dense structural CFOG matcher and enter the sensors and resolutions: 78.32 metres for IIRS and 19.6 metres for TMC-2. Then execute.

*(pause while it runs, about 6 to 12 seconds)* You can see each stage in the log as it runs.

**[SCREEN]** Results scroll into view. Point at the metric cards, then drag the split slider and try **Difference map**.

Done. *(read off the screen)* About 98 of 100 correspondences verified, RMSE around 0.7 pixels, full coverage of the overlap, and the decision is **ACCEPTED**. Every number here was computed from this run.

Drag the split slider and you can see the craters line up across the two sensors.

### Correspondences (9:55 – 10:15)

**[SCREEN]** Click **Correspondences**. Hover over a few points.

The correspondences tab shows the actual matched points from this run: inliers in green, outliers in red. Hover over any point to see its coordinates and residual.

### Fail-safe (10:15 – 10:45)

**[SCREEN]** Back to **Studio**. Upload the two unrelated images and run.

Finally, the safety check. I'll give it two images that don't belong together.

*(after the run)* The result is **NOT RELIABLE**, and it lists exactly which criteria failed. LunarMatch doesn't invent a transform. It tells you it couldn't find one.

---

# CLOSING (11:00 – 11:20)

**[SCREEN]** Back to the PPT title slide, or the website Overview.

So that's LunarMatch. It registers real Chandrayaan-2 cross-sensor imagery on a CPU, measures every result, and refuses to hand over a transform it can't stand behind.

Thank you for watching. We're Team Spectrum, Smart India Hackathon 2026.

---

## If something goes wrong while recording

| Problem | What to do |
| :--- | :--- |
| Header says FLIGHT SIMULATION | Backend isn't reachable. Start it, then click **CHECK**. Don't record the Studio part in simulation mode while saying "real data". |
| Studio run is slow | First run warms up; do a practice run before recording. Make sure Dense CFOG and both GSDs are set. |
| Mobile app shows offline | Emulator needs `http://10.0.2.2:8000`; a phone needs your PC's LAN IP. Set it on the **About** screen. |
| Numbers differ from this script | That's fine. Read what's on screen. |
| Running over time | Cut the mobile Robustness lab and the website fail-safe first. |

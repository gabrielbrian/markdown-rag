# Remote Sensing — 500-line test document

<!-- This markdown file is structured so an agent that splits by header will produce 50 chunks. Each chunk starts with an H2 header and contains 9 short lines (sentences). Total lines = 50 * 10 = 500. -->

<!-- Section block format: ## Section N: <topic>\nline1\nline2...line9 -->

## Section 1: Sensors and Platforms

Optical sensors measure reflected sunlight from Earth's surface.
Multispectral imagers capture several discrete spectral bands.
Hyperspectral sensors record hundreds of narrow contiguous bands.
Synthetic Aperture Radar (SAR) senses surface structure through microwaves.
LiDAR systems emit laser pulses to measure precise elevation.
UAVs provide flexible low-altitude remote sensing capabilities.
Satellite platforms offer global, repeated coverage over time.
Airborne platforms bridge between satellites and UAVs for resolution.
Sensor selection depends on spatial, spectral, temporal, and radiometric needs.

## Section 2: Spatial Resolution and Scale

Spatial resolution defines the ground area represented by a pixel.
High spatial resolution reveals small features like buildings and trees.
Medium resolution is useful for agriculture and landscape mapping.
Coarse resolution supports climate studies and global monitoring.
Scale considerations affect the choice of classification methods.
Mixed pixels occur when multiple land covers fall within a pixel.
Resampling changes apparent spatial resolution and can introduce artifacts.
Trade-offs exist between coverage area and achievable spatial detail.
Spatial resolution interacts with sensor noise and radiometric quality.

## Section 3: Spectral Resolution and Bands

Spectral resolution describes the width and number of spectral bands.
Panchromatic bands capture broad-spectrum intensity at high detail.
Red, green, and blue bands produce natural-color composites.
Near-infrared bands are sensitive to vegetation health and biomass.
Shortwave infrared (SWIR) helps distinguish soil and moisture content.
Thermal infrared measures emitted radiation related to temperature.
Hyperspectral data enable material identification via spectral signatures.
Band selection is crucial for indices like NDVI or water detection.
Sensor spectral response functions affect quantitative analyses.

## Section 4: Temporal Resolution and Revisit Time

Temporal resolution is how often a sensor revisits the same location.
High revisit frequency supports monitoring of rapid changes.
Cloud cover can effectively reduce useful temporal resolution.
Constellations of small satellites can increase revisit rates.
Time-series analysis requires consistent acquisition geometry and calibration.
Phenology studies leverage seasonal temporal resolution to track growth.
Event detection benefits from near-real-time or daily imagery.
Revisit time trade-offs involve cost, data volume, and processing needs.
Temporal fusion combines datasets with different revisit characteristics.

## Section 5: Radiometric Resolution and Calibration

Radiometric resolution is the sensitivity to incoming signal strength.
Higher radiometric resolution captures finer differences in brightness.
Calibration converts raw sensor counts to physical units like radiance.
Radiometric calibration can be absolute or relative between scenes.
Dark object subtraction is a simple radiometric correction approach.
Vicarious calibration uses ground targets of known reflectance.
Sensor degradation over time requires ongoing radiometric monitoring.
Stray light and sensor nonlinearity can bias radiometric measurements.
Well-calibrated radiometry is critical for quantitative remote sensing.

## Section 6: Atmospheric Effects and Correction

Atmospheric gases and aerosols scatter and absorb radiation en route.
Atmospheric correction recovers surface reflectance from TOA radiance.
Simple methods include dark object subtraction and empirical line calibration.
Physics-based approaches use radiative transfer models like 6S.
Water vapor and aerosols strongly affect shortwave and thermal bands.
Topographic shadows complicate atmospheric correction in mountainous areas.
Accurate atmospheric data improve the retrieval of surface properties.
Atmospheric correction is essential for multi-date and multi-sensor comparisons.
Validation uses ground measurements or cross-sensor comparisons.

## Section 7: Georeferencing and Orthorectification

Georeferencing assigns geographic coordinates to image pixels.
Ground control points (GCPs) improve geolocation accuracy.
Orthorectification corrects terrain-related displacement using a DEM.
Without orthorectification, planimetric measurements are biased.
RPCs (rational polynomial coefficients) are commonly used for geolocation.
Map projections determine how coordinates are represented on a flat map.
Datum mismatches lead to systematic spatial misalignment.
Image-to-map registration is fundamental for multi-source fusion.
Assessing geolocation error guides downstream positional uncertainty.

## Section 8: Digital Elevation Models (DEM)

DEMs represent Earth's surface elevation as a raster grid.
LiDAR and stereo photogrammetry are common DEM generation methods.
DEM quality affects orthorectification and hydrological modeling.
Vertical accuracy of DEMs varies with sensor and processing method.
Slope and aspect derived from DEMs assist in terrain analysis.
DEMs are used to correct for topographic illumination effects.
Digital Surface Models (DSM) include vegetation and built features.
Bare-earth DEM extraction often requires filtering of non-ground returns.
Open DEM sources include SRTM, ASTER GDEM, and national LiDAR products.

## Section 9: Image Preprocessing Steps

Preprocessing often includes radiometric and geometric corrections.
Cloud masking removes pixels contaminated by clouds and shadows.
Noise reduction can use spatial filters or temporal compositing.
Atmospheric correction yields surface reflectance for many analyses.
Subsetting and mosaicking combine multiple scenes into a continuous map.
Gap-filling addresses missing data due to clouds or sensor issues.
Normalization harmonizes data from different dates or sensors.
Quality flags in metadata help automate preprocessing workflows.
Reformatting and reprojection prepare data for analysis pipelines.

## Section 10: Indices for Vegetation and Land

NDVI contrasts near-infrared and red to indicate vegetation vigor.
EVI improves sensitivity in high-biomass and aerosol-prone areas.
SAVI compensates for soil brightness in sparse vegetation regions.
NDWI targets water features by combining NIR and SWIR bands.
NDSI helps detect snow and ice by leveraging green and SWIR bands.
Chlorophyll indices estimate photosynthetic pigment concentrations.
Index choice depends on vegetation type, season, and sensor bands.
Spectral indices simplify multispectral data into interpretable metrics.
Indices are widely used for agriculture, forestry, and land monitoring.

## Section 11: SAR Basics and Advantages

SAR actively transmits microwaves and records backscatter signals.
SAR can operate day or night and through many weather conditions.
Backscatter depends on surface roughness, moisture, and geometry.
Polarization (HH, VV, HV, VH) provides insight into scattering mechanisms.
Interferometry (InSAR) measures surface displacement and topography.
SAR resolution improves with longer synthetic apertures and processing.
Speckle is an inherent SAR noise that requires filtering techniques.
SAR complementarity with optical sensors boosts interpretation.
Wavelength (X, C, L, P band) affects penetration and sensitivity.

## Section 12: SAR Interferometry and Applications

InSAR measures phase differences between two SAR acquisitions.
Small baseline subsets reduce temporal decorrelation in interferograms.
Differential InSAR detects subsidence, uplift, and landslide motion.
Persistent Scatterer Interferometry tracks stable point targets over time.
Polarimetric SAR interferometry combines polarization and phase analysis.
Atmospheric phase delays can confound InSAR deformation signals.
Coherence maps indicate areas of reliable interferometric phase.
Time-series InSAR needs careful unwrapping and noise mitigation.
InSAR is essential for geohazard monitoring and infrastructure checks.

## Section 13: LiDAR Point Clouds and Processing

LiDAR returns produce dense 3D point clouds of surface structure.
Point classification separates ground, vegetation, and buildings.
Canopy height models derive vegetation height from DSM and DEM subtraction.
Point density determines the level of detail in derived products.
Full-waveform LiDAR captures energy distribution along the return pulse.
Multispectral LiDAR adds spectral information to geometric returns.
Point cloud registration combines multiple flight lines into one dataset.
Voxelization and gridding convert point clouds into raster products.
LiDAR supports forestry inventory, urban modeling, and flood mapping.

## Section 14: Hyperspectral Analysis and Spectral Unmixing

Hyperspectral data allow fine discrimination of materials by spectrum.
Spectral libraries catalog known materials' reflectance signatures.
Spectral unmixing decomposes pixel spectra into fractional abundances.
Endmember selection is critical for accurate unmixing results.
Dimensionality reduction (PCA, MNF) helps remove noise and redundancy.
Continuum removal enhances diagnostic absorption features.
Hyperspectral anomalies can indicate minerals or stressed vegetation.
Calibration to reflectance improves comparability across dates and sensors.
Hyperspectral data require careful preprocessing for atmospheric effects.

## Section 15: Data Fusion and Multisensor Integration

Data fusion combines strengths of optical, SAR, and LiDAR sources.
Spatial data fusion can pan-sharpen multispectral imagery using panchromatic bands.
Temporal fusion merges frequent low-resolution with infrequent high-resolution data.
Feature-level fusion concatenates descriptors before classification.
Decision-level fusion merges results from independent classifiers.
Co-registration accuracy is crucial before any fusion step.
Sensor-specific noise and artifacts must be accounted for in fusion.
Cross-sensor radiometric normalization improves fused-product quality.
Data fusion enables richer insights than single-sensor analysis alone.

## Section 16: Classification Methods Overview

Supervised classification uses labeled training data for learning.
Unsupervised classification groups pixels by spectral similarity.
Object-based image analysis segments images into meaningful objects.
Machine learning classifiers include random forests and SVMs.
Deep learning models (CNNs) learn hierarchical spatial-spectral features.
Transfer learning adapts pre-trained models to new remote sensing tasks.
Ensemble methods combine multiple classifiers for improved robustness.
Feature engineering remains important for traditional classifiers.
Accuracy assessment validates classification with independent reference data.

## Section 17: Change Detection Techniques

Change detection identifies land-cover transitions across time.
Image differencing subtracts band values or indices between dates.
Time series decomposition separates trend, seasonal, and residual components.
Trajectory-based methods detect gradual or abrupt changes in pixels.
Post-classification comparison assesses categorical class changes.
Change vector analysis inspects magnitude and direction of spectral change.
Threshold selection and noise filtering influence detection sensitivity.
Validation requires temporal ground truth or high-confidence reference imagery.
Change detection supports deforestation, urban expansion, and disaster response.

## Section 18: Accuracy Assessment and Validation

Confusion matrices summarize classification performance by class.
Overall accuracy, user's and producer's accuracies quantify errors.
Kappa statistic measures agreement beyond chance, with caveats.
Sampling design for validation impacts the reliability of accuracy estimates.
Independent validation data reduces optimistic bias in reported accuracy.
Cross-validation helps evaluate model generalizability in limited datasets.
Error propagation should be considered in multi-step processing chains.
Reporting confidence intervals gives transparency about result certainty.
Ground truth collection should match the spatial and temporal scale of imagery.

## Section 19: Object Detection and Segmentation

Object detection locates instances of target objects in imagery.
Instance segmentation delineates object boundaries at pixel level.
Anchor-based and anchor-free detectors offer different trade-offs.
Mask R-CNN is a common architecture for segmentation tasks.
Training requires annotated bounding boxes or pixel masks for targets.
Data augmentation helps prevent overfitting in deep models.
Post-processing refines detections with non-maximum suppression and filtering.
Evaluation metrics include mAP, IoU, precision, and recall for objects.
Object-level analysis supports infrastructure mapping and crop counting.

## Section 20: Time Series and Phenology

Remote sensing time series capture seasonal cycles and

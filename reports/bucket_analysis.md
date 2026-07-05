# GCS Bucket Analysis Reports

**Generated:** 2026-07-04 22:47 UTC  
**Folder:** `enc-techint-datasets-gc` (`dab24f50-81ba-4906-815b-cf2aced60f71`)  

---

## 1. Content Overview

| Metric | Value |
|--------|-------|
| Total items | 110,000 |
| Total size | 2.8 GB |
| Image files | 10,000 |
| JSON annotation files | 100,000 |

### File Type Details

| Type | Count | Total Size | Avg Size | Min Size | Max Size |
|------|------:|----------:|--------:|--------:|--------:|
| image | 10,000 | 1.0 GB | 109.9 KB | 23.1 KB | 480.9 KB |
| json_text | 100,000 | 1.7 GB | 17.9 KB | 2.3 KB | 67.7 KB |

### MIME Type Distribution

| MIME Type | Count |
|-----------|------:|
| `application/json` | 100,000 |
| `image/jpeg` | 10,000 |

### Image Resolution Distribution

| Resolution | Count |
|-----------|------:|
| 1280x720 | 9,990 |
| 720x1280 | 10 |

---

## 2. Annotation Coverage

| Metric | Count | Share |
|--------|------:|------:|
| Total images | 10,000 | 100% |
| **With annotation data** | **4,260** | **42.6%** |
| Without annotation data | 5,740 | 57.4% |

<details><summary>Sample unannotated images (first 20)</summary>

- `ds-challenge-bddfde26/10k/test/ac517380-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ac56c836-bdabca21.jpg`
- `ds-challenge-bddfde26/10k/test/ac6d4f42-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ac6e638d-7c84846d.jpg`
- `ds-challenge-bddfde26/10k/test/ac73d367-0cb39ad0.jpg`
- `ds-challenge-bddfde26/10k/test/ac985232-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ac9be3fe-790d1f8e.jpg`
- `ds-challenge-bddfde26/10k/test/aca32929-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/aca4b150-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/acaaf824-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ace9bf57-669189d2.jpg`
- `ds-challenge-bddfde26/10k/test/ad522266-1f8f3ba4.jpg`
- `ds-challenge-bddfde26/10k/test/ad9f7908-42ec4c0e.jpg`
- `ds-challenge-bddfde26/10k/test/ada0552e-51d73d3c.jpg`
- `ds-challenge-bddfde26/10k/test/ae1305f8-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ae49bf6d-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ae4b0c67-4607fe51.jpg`
- `ds-challenge-bddfde26/10k/test/ae5f775e-0abb299c.jpg`
- `ds-challenge-bddfde26/10k/test/ae60618a-00000000.jpg`
- `ds-challenge-bddfde26/10k/test/ae6a0a72-00000000.jpg`

</details>

---

## 3. Category Distribution

| Metric | Value |
|--------|-------|
| JSON files analysed | 100,000 |
| Files containing objects | 100,000 |
| Total objects parsed | 2,777,733 |
| Distinct categories | 21 |

| Category | Object Count | Share |
|----------|-------------:|------:|
| `car` | 1,021,811 | 36.8% |
| `lane/single white` | 353,334 | 12.7% |
| `traffic sign` | 343,882 | 12.4% |
| `traffic light` | 266,032 | 9.6% |
| `lane/road curb` | 157,406 | 5.7% |
| `lane/crosswalk` | 154,228 | 5.6% |
| `person` | 129,350 | 4.7% |
| `area/drivable` | 91,625 | 3.3% |
| `area/alternative` | 88,379 | 3.2% |
| `lane/double yellow` | 53,449 | 1.9% |
| `truck` | 42,963 | 1.5% |
| `lane/single yellow` | 28,962 | 1.0% |
| `bus` | 16,502 | 0.6% |
| `bike` | 10,232 | 0.4% |
| `lane/double white` | 8,206 | 0.3% |
| `rider` | 6,465 | 0.2% |
| `motor` | 4,295 | 0.2% |
| `lane/single other` | 394 | 0.0% |
| `train` | 179 | 0.0% |
| `lane/double other` | 37 | 0.0% |
| `area/unknown` | 2 | 0.0% |

---

## 4. Frame-Level Attributes

| Metric | Value |
|--------|-------|
| Files with frame attributes | 100,000 |
| Total frames parsed | 100,000 |
| Distinct frame attribute types | 3 |

### `scene`

Distinct values: **7**

| Value | Count | Share |
|-------|------:|------:|
| `city street` | 61,981 | 62.0% |
| `highway` | 24,982 | 25.0% |
| `residential` | 11,740 | 11.7% |
| `parking lot` | 535 | 0.5% |
| `undefined` | 517 | 0.5% |
| `tunnel` | 205 | 0.2% |
| `gas stations` | 40 | 0.0% |

### `timeofday`

Distinct values: **4**

| Value | Count | Share |
|-------|------:|------:|
| `daytime` | 52,504 | 52.5% |
| `night` | 39,993 | 40.0% |
| `dawn/dusk` | 7,287 | 7.3% |
| `undefined` | 216 | 0.2% |

### `weather`

Distinct values: **7**

| Value | Count | Share |
|-------|------:|------:|
| `clear` | 53,514 | 53.5% |
| `overcast` | 12,591 | 12.6% |
| `undefined` | 11,631 | 11.6% |
| `snowy` | 7,891 | 7.9% |
| `rainy` | 7,127 | 7.1% |
| `partly cloudy` | 7,065 | 7.1% |
| `foggy` | 181 | 0.2% |

---

## 5. Object-Level Attributes

**Distinct object attribute types:** 5

### `direction`

Distinct values: **2**

| Value | Count | Share |
|-------|------:|------:|
| `parallel` | 562,162 | 20.2% |
| `vertical` | 193,854 | 7.0% |

### `occluded`

Distinct values: **2**

| Value | Count | Share |
|-------|------:|------:|
| `False` | 970,498 | 34.9% |
| `True` | 871,213 | 31.4% |

### `style`

Distinct values: **2**

| Value | Count | Share |
|-------|------:|------:|
| `solid` | 427,198 | 15.4% |
| `dashed` | 328,818 | 11.8% |

### `trafficLightColor`

Distinct values: **4**

| Value | Count | Share |
|-------|------:|------:|
| `none` | 1,656,020 | 59.6% |
| `green` | 114,182 | 4.1% |
| `red` | 66,468 | 2.4% |
| `yellow` | 5,041 | 0.2% |

### `truncated`

Distinct values: **2**

| Value | Count | Share |
|-------|------:|------:|
| `False` | 1,714,230 | 61.7% |
| `True` | 127,481 | 4.6% |

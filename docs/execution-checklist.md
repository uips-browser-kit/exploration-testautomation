# Execution Checklist

Reference: [Tracking issue #1](https://github.com/uips-browser-kit/exploration-testautomation/issues/1)

## Solution Design Baseline

### A. Problem framing
- [ ] [#33 Design baseline A: Problem framing](https://github.com/uips-browser-kit/exploration-testautomation/issues/33)

### B. Architecture boundaries
- [ ] [#34 Design baseline B: Architecture boundaries](https://github.com/uips-browser-kit/exploration-testautomation/issues/34)

### C. Contract-first design
- [ ] [#35 Design baseline C: Contract-first design](https://github.com/uips-browser-kit/exploration-testautomation/issues/35)

### D. Scenario model design
- [ ] [#36 Design baseline D: Scenario model design](https://github.com/uips-browser-kit/exploration-testautomation/issues/36)

### E. Execution pipeline design
- [ ] [#37 Design baseline E: Execution pipeline design](https://github.com/uips-browser-kit/exploration-testautomation/issues/37)

### F. Reliability and failure strategy
- [ ] [#38 Design baseline F: Reliability and failure strategy](https://github.com/uips-browser-kit/exploration-testautomation/issues/38)

### G. Observability and artifacts
- [ ] [#39 Design baseline G: Observability and artifacts](https://github.com/uips-browser-kit/exploration-testautomation/issues/39)

### H. Parity design across frameworks
- [ ] [#40 Design baseline H: Parity design across frameworks](https://github.com/uips-browser-kit/exploration-testautomation/issues/40)

### I. Test strategy design
- [ ] [#41 Design baseline I: Test strategy design](https://github.com/uips-browser-kit/exploration-testautomation/issues/41)

### J. Change management
- [ ] [#42 Design baseline J: Change management](https://github.com/uips-browser-kit/exploration-testautomation/issues/42)

## Delivery Tracking (Issue-backed)

## 1. Finalize contracts
- [ ] [#2 Define scenario contract specification](https://github.com/uips-browser-kit/exploration-testautomation/issues/2)
- [ ] [#3 Define run-result JSON contract](https://github.com/uips-browser-kit/exploration-testautomation/issues/3)
- [ ] [#4 Add baseline scenarios](https://github.com/uips-browser-kit/exploration-testautomation/issues/4)

## 2. Build core logic
- [ ] [#5 Implement lookup interface (api/cdp/fallback)](https://github.com/uips-browser-kit/exploration-testautomation/issues/5)
- [ ] [#6 Implement candidate selector (random/index)](https://github.com/uips-browser-kit/exploration-testautomation/issues/6)
- [ ] [#7 Implement detail URL builder from template](https://github.com/uips-browser-kit/exploration-testautomation/issues/7)

## 3. Ship first vertical slice
- [ ] [#8 Implement Playwright reference flow](https://github.com/uips-browser-kit/exploration-testautomation/issues/8)

## 4. Lock reliability
- [ ] [#14 Add scenario contract validation tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/14)
- [ ] [#15 Add run-result contract validation tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/15)
- [ ] [#16 Add determinism tests for selection](https://github.com/uips-browser-kit/exploration-testautomation/issues/16)
- [ ] [#18 Add URL template builder tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/18)

## 5. Parity across frameworks
- [ ] [#9 Implement Puppeteer reference flow](https://github.com/uips-browser-kit/exploration-testautomation/issues/9)
- [ ] [#10 Implement Selenium reference flow](https://github.com/uips-browser-kit/exploration-testautomation/issues/10)
- [ ] [#19 Add framework smoke tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/19)
- [ ] [#20 Add artifact existence tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/20)

## 6. Failure and replay robustness
- [ ] [#17 Add lookup behavior tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/17)
- [ ] [#21 Add replay tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/21)
- [ ] [#22 Add negative-path tests](https://github.com/uips-browser-kit/exploration-testautomation/issues/22)

## 7. Packaging and operations
- [ ] [#12 Add template-aligned pyproject.toml for uv shared venv](https://github.com/uips-browser-kit/exploration-testautomation/issues/12)
- [ ] [#25 Add pinned browser version install and verification](https://github.com/uips-browser-kit/exploration-testautomation/issues/25)
- [ ] [#23 Add CI smoke workflow](https://github.com/uips-browser-kit/exploration-testautomation/issues/23)
- [ ] [#13 Document quickstart and command matrix](https://github.com/uips-browser-kit/exploration-testautomation/issues/13)
- [ ] [#11 Define artifact folder and naming conventions](https://github.com/uips-browser-kit/exploration-testautomation/issues/11)
- [ ] [#24 Plan migration path to shared testdata repo](https://github.com/uips-browser-kit/exploration-testautomation/issues/24)

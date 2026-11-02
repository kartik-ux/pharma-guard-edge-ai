# PHARMA-GUARD Edge AI
## Future Telit Cinterion Hardware Integration Plan

**Project status:** Software prototype developed; hardware integration proposed and pending validation.

## 1. Overview

PHARMA-GUARD Edge AI is a prototype for monitoring pharmaceutical cold-chain shipments. It analyses telemetry to identify temperature excursions and unusual environmental patterns.

The current prototype uses synthetic telemetry. Integration with Telit Cinterion hardware is a proposed next development stage and has not yet been validated on a physical device.

The objective is to establish a reliable edge-to-application architecture that can collect sensor data, evaluate shipment conditions and provide actionable monitoring information.

## 2. Proposed Architecture

The proposed system architecture is:

1. **Environmental sensors:** Collect temperature and, where supported, humidity, light exposure and acceleration data.
2. **Telit Cinterion device:** Provides the available sensor interfaces and communication capabilities, depending on the selected hardware model.
3. **Communication layer:** Transfers telemetry using a protocol supported by the selected device, such as MQTT, HTTPS or a suitable serial interface.
4. **Edge gateway:** Runs on compatible hardware if the Telit device does not support the Python runtime or inference workload required by PHARMA-GUARD.
5. **PHARMA-GUARD processing:** Validates incoming telemetry, applies configurable risk rules and executes the Isolation Forest anomaly-detection model.
6. **Data and monitoring layer:** Stores readings and exposes shipment information through the FastAPI backend and monitoring dashboard.

## 3. Hardware Assessment

The following details must be confirmed against the selected Telit Cinterion hardware and its official documentation.

| Area | Information to validate |
|---|---|
| Hardware | Exact device model and revision |
| Firmware | Firmware version and supported SDK |
| Sensors | Available environmental sensor interfaces |
| Interfaces | UART, USB, I2C, SPI or GPIO, where supported |
| Connectivity | Cellular, Wi-Fi, Ethernet or other available connectivity |
| Protocols | Supported MQTT, HTTPS, TCP/IP or serial communication |
| Edge compute | Available CPU, memory, storage and runtime support |
| Security | Device authentication, encryption and credential management |
| Power | Battery characteristics and expected operating lifetime |

No hardware capabilities are assumed until the selected device and its documentation have been verified.

## 4. Proposed Integration Components

### 4.1 Sensor Acquisition

The acquisition layer will collect environmental readings from compatible sensors. Sensor availability and sampling frequency will depend on the selected hardware.

### 4.2 Device Communication Adapter

A dedicated adapter will translate device-specific messages into the application's internal telemetry format. This will keep the PHARMA-GUARD processing pipeline independent of the underlying hardware protocol.

### 4.3 Edge Processing

The edge-processing layer will perform:

- Telemetry validation and normalisation.
- Configurable temperature-excursion checks.
- Risk-score calculation.
- Isolation Forest anomaly detection.
- Event generation for abnormal readings.

If the selected Telit device cannot support the required Python environment, processing will be deployed on a compatible external edge gateway.

### 4.4 Monitoring and Storage

The existing FastAPI backend, SQLite persistence and dashboard will provide the initial application layer. The storage architecture can be extended for production deployment after integration requirements are established.

## 5. Proposed Canonical Telemetry Format

The following JSON is an example of the internal PHARMA-GUARD telemetry format. It is not a claim about the native Telit Cinterion payload.

```json
{
  "device_id": "edge-device-001",
  "shipment_id": "shipment-001",
  "timestamp": "2026-11-02T12:00:00Z",
  "temperature_c": 5.2,
  "humidity_percent": 48.5,
  "light_exposure": false,
  "acceleration_g": 0.12,
  "battery_percent": 92
}
```

The adapter will map verified device messages into this schema. Optional fields will be included only when supported by the connected sensors.

## 6. Data Flow

1. Sensors collect environmental measurements.
2. The selected Telit device acquires or transmits the available readings.
3. The communication adapter receives and validates the telemetry.
4. The edge-processing layer evaluates risk and anomaly indicators.
5. Results are stored and made available through the FastAPI service.
6. The dashboard displays shipment conditions and detected events.

## 7. Security and Reliability

The integration should consider:

- Authenticated device communication.
- Encryption in transit where supported.
- Secure storage of credentials.
- Input validation and timestamp checks.
- Handling of missing, delayed or duplicated readings.
- Network interruption and reconnection behaviour.
- Local buffering where supported.
- Audit-friendly event and processing logs.

These controls are proposed design requirements and will need implementation and testing.

## 8. Testing and Validation Plan

The hardware integration will be validated in stages:

1. Confirm device identity, firmware and documentation.
2. Verify sensor readings against reference measurements.
3. Test the communication interface and telemetry mapping.
4. Compare edge-processing results with the existing software prototype.
5. Test abnormal readings and simulated temperature excursions.
6. Test network interruptions, recovery and data integrity.
7. Measure inference latency, memory usage and power consumption.
8. Evaluate performance using representative, labelled data.

Synthetic-data results from the current prototype must not be interpreted as validated real-world performance.

## 9. Development Roadmap

| Phase | Planned activity |
|---|---|
| Phase 1 | Identify the Telit Cinterion device and review its technical documentation |
| Phase 2 | Confirm sensor compatibility and communication interfaces |
| Phase 3 | Implement the device communication adapter |
| Phase 4 | Deploy processing on the device or a compatible edge gateway |
| Phase 5 | Integrate with FastAPI, storage and dashboard |
| Phase 6 | Perform hardware, reliability and performance validation |

## 10. Open Technical Questions

The following information is required before implementation:

- Which exact Telit Cinterion device or development kit will be used?
- Which environmental sensors are available?
- What communication interfaces and protocols are supported?
- Can the device run custom Python applications, or is an external gateway required?
- What SDK, firmware and development tools are available?
- What are the device's power, memory and processing constraints?
- What are the expected connectivity and data-retention requirements?

## 11. Expected Outcome

The intended outcome is a hardware-integrated cold-chain monitoring prototype that combines sensor telemetry, edge-based risk analysis, anomaly detection and shipment monitoring.

The final architecture and deployment approach will be determined by the capabilities of the selected Telit Cinterion hardware and the results of physical validation.

**Integration status:** Proposed. Physical hardware integration, device compatibility and real-world performance remain to be verified.

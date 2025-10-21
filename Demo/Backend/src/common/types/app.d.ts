export interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export interface TelemetryData {
  Timestamp: number;
  scan: boolean;
  PosX: number;
  PosY: number;
  PosZ: number;
  RotX: number;
  RotY: number;
  RotZ: number;
  Joint0RotX: number;
  Joint0RotY: number;
  Joint0RotZ: number;
  Joint1RotX: number;
  Joint1RotY: number;
  Joint1RotZ: number;
}

export interface ReconstructionParameters {
  depth: number;
  boundary: number;
}

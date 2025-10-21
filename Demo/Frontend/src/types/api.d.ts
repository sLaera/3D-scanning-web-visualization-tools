export interface ApiResponse<T> {
  error: string | null
  data: T | null
}

export interface Vector3 {
  x: number
  y: number
  z: number
}

export interface TelemetryData {
  Position: Vector3
  Rotation: Vector3
  Timestamp: number
  ScanFrame: boolean
  ArmJoint0Rotation: Vector3
  ArmJoint1Rotation: Vector3
}

export interface ReconstructDto {
  recompute: boolean
  modelName: string
}

export interface ModelDiffDto {
  modelName: string
  positiveBreakpoints: number[]
  negativeBreakpoints: number[]
  recompute: boolean
}

export interface ModelDiffInfo {
  sourceMesh: string
  targetMesh: string
  pointsTexture: string
  positionsTexture: string
}

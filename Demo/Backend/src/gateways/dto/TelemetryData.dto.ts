import { Vector3 } from '../../common/types/app';

export default class TelemetryDataDto {
  public Position: Vector3;
  public Rotation: Vector3;
  public Timestamp: number;
  public ScanFrame: boolean;
  public ArmJoint0Rotation: Vector3;
  public ArmJoint1Rotation: Vector3;
}

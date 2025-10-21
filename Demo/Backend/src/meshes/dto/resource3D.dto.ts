import { IsString, IsNotEmpty, IsEnum, IsBoolean } from 'class-validator';

export enum MeshType {
  GLTF,
  POINT_CLOUD,
}

export default class Resource3D {
  @IsString()
  @IsNotEmpty()
  url: string;

  @IsString()
  @IsNotEmpty()
  name: string;

  @IsEnum(MeshType)
  type: MeshType;

  @IsBoolean()
  isReconstructed?: boolean = false;
}

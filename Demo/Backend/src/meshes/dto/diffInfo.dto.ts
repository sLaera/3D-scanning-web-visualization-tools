import { IsNotEmpty, IsString } from 'class-validator';

export default class DiffInfoDto {
  @IsString()
  @IsNotEmpty()
  sourceMesh: string;

  @IsString()
  @IsNotEmpty()
  targetMesh: string;

  @IsString()
  @IsNotEmpty()
  pointsTexture: string;

  @IsString()
  @IsNotEmpty()
  positionsTexture: string;
}

import { Controller, Get, Post, Req } from '@nestjs/common';
import { MeshesService } from './meshes.service';
import Resource3D from './dto/resource3D.dto';
import { Request } from 'express';
import DiffInfoDto from './dto/diffInfo.dto';
import ModelDiffDto from './dto/ModelDiffDto';
import ReconstructDto from './dto/ReconstructDto';

@Controller('meshes')
export class MeshesController {
  constructor(private readonly meshesService: MeshesService) {}

  /**
   * Return all the available meshes
   */
  @Get('/')
  findAll(@Req() request: Request): Promise<Resource3D[]> {
    return this.meshesService.findAll(request);
  }

  @Post('/reconstruct')
  reconstruct(@Req() request: Request): Promise<string> {
    const body: ReconstructDto = request.body;
    return this.meshesService.reconstruct(
      body.recompute,
      body.modelName,
      request,
    );
  }

  @Post('/generate-difference')
  generateDifference(@Req() request: Request): Promise<DiffInfoDto> {
    const body: ModelDiffDto = request.body;
    return this.meshesService.generateDiffModel(
      body.modelName,
      body.positiveBreakpoints,
      body.negativeBreakpoints,
      body.recompute,
      request,
    );
  }
}

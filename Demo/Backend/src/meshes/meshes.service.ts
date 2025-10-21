import { Inject, Injectable } from '@nestjs/common';
import Resource3D, { MeshType } from './dto/resource3D.dto';
import { Request } from 'express';
import * as fs from 'fs';
import { ReconstructionParameters } from '../common/types/app';
import DiffInfoDto from './dto/diffInfo.dto';
import { spawnAsync } from '../utils';
import * as path from 'node:path';

//dummy data
const dummyMeshes = [
  {
    localUrl: '/models/Target.glb',
    name: 'Target',
    type: MeshType.GLTF,
  },
  {
    localUrl: '/models/Target-no-solar.glb',
    name: 'Target missing panels',
    type: MeshType.GLTF,
  },
];

@Injectable()
export class MeshesService {
  constructor(
    @Inject('TO_RECONSTRUCT_FILE_PATH')
    private toReconstructFilePath: string,
    @Inject('RECONSTRUCTED_FILE_PATH')
    private reconstructedFilePath: string,
    @Inject('SPSR_PATH')
    private spsrPath: string,
    @Inject('RECONSTRUCT_SCRIPT_PATH')
    private reconstructScriptPath: string,
    @Inject('SPSR_PARAMS_FILE_PATH')
    private spsrParamsPath: string,
    @Inject('MODEL_DIFF_PATH')
    private modelDiffPath: string,
    @Inject('OUTPUT_MODEL_DIFF_PATH')
    private outputModelDiffPath: string,
    @Inject('PUBLIC_PATH')
    private publicPath: string,
  ) {}

  async findAll(req: Request): Promise<Resource3D[]> {
    const rootUrl = `${req.protocol}://${req.get('host')}`;
    //set url values so it has host info
    return dummyMeshes.map((m) =>
      Object.assign(new Resource3D(), {
        url: `${rootUrl}${m.localUrl}`,
        name: m.name,
      }),
    );
  }

  /**
   * Reconstructs the off file generated during the simulation step.
   * Return the url of the reconstructed obj
   */
  async reconstruct(
    recompute: boolean,
    modelName: string,
    request: Request,
  ): Promise<string> {
    modelName = modelName.replaceAll(' ', '_');
    if (!this.doNotRecompute(recompute, modelName)) {
      //reconstruct only if necessary or the recompute flag is true
      await this.readParamsAndRemesh(this.spsrParamsPath);
    }

    const rootUrl = `${request.protocol}://${request.get('host')}`;
    return `${rootUrl}/reconstruction/reconstructed.obj`; //todo: do not hardcode
  }

  /**
   * Read params from a configuration file and execute remesh function
   * @param filePath Parameter file path
   * @returns resolve promise after remesh execution
   */
  private async readParamsAndRemesh(filePath: string): Promise<void> {
    if (!fs.existsSync(filePath)) {
      throw new Error(`Cannot find file: ${filePath}`);
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    let readValues: ReconstructionParameters;
    try {
      // Parse parameters. Fix single quote in file content
      readValues = JSON.parse(content.replace(/'/g, '"'));
    } catch (e) {
      throw new Error(`Cannot parse file ${filePath}: ${e}`);
    }
    // Execute reconstruction
    return await this.poissonRemesh(readValues);
  }

  /**
   * Execute remesh with screened poisson
   * @param depth
   * @param boundary
   */
  async poissonRemesh({
    depth = 8,
    boundary = 2,
  }: ReconstructionParameters): Promise<void> {
    const args = [
      this.reconstructScriptPath,
      '--poisson_recon_exe',
      this.spsrPath,
      '--input',
      this.toReconstructFilePath,
      '--out',
      this.reconstructedFilePath,
      '--depth',
      depth.toString(),
      '--bType',
      boundary.toString(),
    ];

    const startTime = Date.now();
    try {
      await spawnAsync('python', args);
      console.log('Execution time:', (Date.now() - startTime) / 1000);
    } catch (error) {
      throw new Error(
        `Cannot execute command: python ${args.join(' ')}\nError: ` +
          error.toString(),
      );
    }
  }

  async generateDiffModel(
    modelName: string,
    positiveBreakpoints: number[],
    negativeBreakpoints: number[],
    recompute: boolean,
    request: Request,
  ): Promise<DiffInfoDto> {
    modelName = modelName.replaceAll(' ', '_');
    const rootUrl = `${request.protocol}://${request.get('host')}`;
    //todo: do not hardcode
    const modelsUrls: DiffInfoDto = {
      sourceMesh: `${rootUrl}/difference/output${modelName}/source.obj`,
      targetMesh: `${rootUrl}/difference/output${modelName}/target.obj`,
      pointsTexture: `${rootUrl}/difference/output${modelName}/points.png`,
      positionsTexture: `${rootUrl}/difference/output${modelName}/positions.png`,
    };

    if (this.doNotRecompute(recompute, modelName)) {
      return modelsUrls;
    }

    const args: string[] = [
      this.modelDiffPath,
      '--source_path',
      path.join(this.publicPath, 'models', 'Target.obj'),
      '--target_path',
      this.reconstructedFilePath,
      '--output_path_dir',
      this.outputModelDiffPath + modelName,
      '--texture_dim',
      '2048',
      '--samples',
      '100000',
      // '--icp',
      '--simplify',
    ];

    if (positiveBreakpoints.length > 0 && negativeBreakpoints.length > 0) {
      args.push(
        '--use_brk',
        '--p_brk1',
        positiveBreakpoints[0].toString(),
        '--p_brk2',
        positiveBreakpoints[1].toString(),
        '--p_brk3',
        positiveBreakpoints[2].toString(),
        '--n_brk1',
        negativeBreakpoints[0].toString(),
        '--n_brk2',
        negativeBreakpoints[1].toString(),
        '--n_brk3',
        negativeBreakpoints[2].toString(),
      );
    }

    try {
      await spawnAsync('python', args);
    } catch (error) {
      throw new Error(
        `Cannot execute command: python ${args.join(' ')}\nError: ` +
          error.toString(),
      );
    }

    return modelsUrls;
  }

  private doNotRecompute(recompute: boolean, modelName: string): boolean {
    //do not recompute difference if already exists
    const localOutputPath = this.outputModelDiffPath + modelName;
    return (
      !recompute &&
      fs.existsSync(localOutputPath + '/source.obj') &&
      fs.existsSync(localOutputPath + '/target.obj') &&
      fs.existsSync(localOutputPath + '/points.png') &&
      fs.existsSync(localOutputPath + '/positions.png')
    );
  }
}

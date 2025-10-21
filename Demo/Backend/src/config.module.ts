import { Module } from '@nestjs/common';

@Module({
  providers: [
    {
      provide: 'TELEMETRY_PATH',
      useValue: `${__dirname}/../externals/mock-telemetry.csv`,
    },
    {
      provide: 'TO_RECONSTRUCT_FILE_PATH',
      useValue: `${__dirname}/../externals/reconstruction/to-reconstruct.off`,
    },
    {
      provide: 'RECONSTRUCTED_FILE_PATH',
      useValue: `${__dirname}/../public/reconstruction/reconstructed.obj`,
    },
    {
      provide: 'SPSR_PATH',
      useValue: `${__dirname}/../externals/reconstruction/PoissonRecon/Bin/Linux/PoissonRecon`,
    },
    {
      provide: 'RECONSTRUCT_SCRIPT_PATH',
      useValue: `${__dirname}/../externals/reconstruction/reconstruct.py`,
    },
    {
      provide: 'SPSR_PARAMS_FILE_PATH',
      useValue: `${__dirname}/../externals/reconstruction/best_params_spsr.txt`,
    },
    {
      provide: 'MODEL_DIFF_PATH',
      useValue: `${__dirname}/../externals/mesh-difference/calculate_difference.py`,
    },
    {
      provide: 'OUTPUT_MODEL_DIFF_PATH',
      useValue: `${__dirname}/../public/difference/output`,
    },
    {
      provide: 'PUBLIC_PATH',
      useValue: `${__dirname}/../public`,
    },
  ],
  exports: [
    'TELEMETRY_PATH',
    'TO_RECONSTRUCT_FILE_PATH',
    'RECONSTRUCTED_FILE_PATH',
    'SPSR_PATH',
    'SPSR_PARAMS_FILE_PATH',
    'MODEL_DIFF_PATH',
    'OUTPUT_MODEL_DIFF_PATH',
    'RECONSTRUCT_SCRIPT_PATH',
    'PUBLIC_PATH'
  ],
})
export class ConfigModule {}

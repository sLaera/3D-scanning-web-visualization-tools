import { Module } from '@nestjs/common';
import { ConfigModule } from '../config.module';
import { MeshesController } from './meshes.controller';
import { MeshesService } from './meshes.service';

@Module({
  imports: [ConfigModule],
  controllers: [MeshesController],
  providers: [MeshesService],
})
export class MeshesModule {}

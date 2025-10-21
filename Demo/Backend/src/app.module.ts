import { Module } from '@nestjs/common';
import { ServeStaticModule } from '@nestjs/serve-static';
import { join } from 'path';
import { ConfigModule } from './config.module';
import { MeshesModule } from './meshes/meshes.module';
import { WebSoketModule } from './gateways/webSoket.module';

@Module({
  imports: [
    ServeStaticModule.forRoot({
      rootPath: join(__dirname, '..', 'public'),
    }),
    WebSoketModule,
    ConfigModule,
    MeshesModule,
  ],
})
export class AppModule {}

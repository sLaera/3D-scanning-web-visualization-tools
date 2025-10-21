import { Module } from '@nestjs/common';
import { TelemetryGateway } from './telemetry.gateway';
import { ConfigModule } from '../config.module';

@Module({
  imports: [ConfigModule],
  providers: [TelemetryGateway],
})
export class WebSoketModule {}

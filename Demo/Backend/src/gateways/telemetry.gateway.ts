import {
  SubscribeMessage,
  WebSocketGateway,
  WebSocketServer,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { Inject } from '@nestjs/common';
import { parse } from 'csv-parse/sync';
import * as fs from 'fs';
import TelemetryDataDto from './dto/TelemetryData.dto';
import { TelemetryData } from '../common/types/app';

@WebSocketGateway({
  cors: {
    origin: '*',
  },
})
export class TelemetryGateway {
  private readonly csvFilePath: string;
  private readonly csvData: TelemetryData[];
  private offFileData: string;

  constructor(
    @Inject('TELEMETRY_PATH')
    telemetryPath: string,
    @Inject('TO_RECONSTRUCT_FILE_PATH')
    private toReconstructFilePath: string,
    @Inject('OUTPUT_MODEL_DIFF_PATH')
    private outputModelDiffPath: string,
  ) {
    this.csvFilePath = telemetryPath;
    this.csvData = this.loadCsvData();
  }

  private loadCsvData(): TelemetryData[] {
    try {
      console.log('Reading Csv file path:', this.csvFilePath);
      const fileContent = fs.readFileSync(this.csvFilePath, 'utf-8');
      return parse(fileContent, {
        columns: true,
        skip_empty_lines: true,
        cast: function (value, context) {
          if (context.header) return value;
          switch (context.column) {
            case 'Timestamp':
            case 'PosX':
            case 'PosY':
            case 'PosZ':
            case 'RotX':
            case 'RotY':
            case 'RotZ':
            case 'Joint0RotX':
            case 'Joint0RotY':
            case 'Joint0RotZ':
            case 'Joint1RotX':
            case 'Joint1RotY':
            case 'Joint1RotZ':
              return parseFloat(value);
            case 'scan':
              return value.toLowerCase() === 'true';
          }
        },
      });
    } catch (error) {
      console.error('Reading CSV Error:', error);
      return [];
    }
  }

  private telemetryToDto(row: TelemetryData): TelemetryDataDto {
    return {
      Position: { x: row.PosX, y: row.PosY, z: row.PosZ },
      Rotation: { x: row.RotX, y: row.RotY, z: row.RotZ },
      Timestamp: row.Timestamp,
      ScanFrame: row.scan,
      ArmJoint0Rotation: {
        x: row.Joint0RotX,
        y: row.Joint0RotY,
        z: row.Joint0RotZ,
      },
      ArmJoint1Rotation: {
        x: row.Joint1RotX,
        y: row.Joint1RotY,
        z: row.Joint1RotZ,
      },
    };
  }

  @WebSocketServer()
  server: Server;

  // ----------------------- lifetime events -----------------------------------
  afterInit() {
    console.log('Initialized');
  }

  handleConnection(client: Socket): void {
    const { sockets } = this.server.sockets;

    console.log(`Client id: ${client.id} connected`);
    console.debug(`Number of connected clients: ${sockets.size}`);
  }

  handleDisconnect(client: Socket): void {
    console.log(`Client id:${client.id} disconnected`);
  }

  // --------- ----------------------------------------------------- -----------

  private timeout(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  @SubscribeMessage('start-stream')
  async streamTelemetry(client: Socket): Promise<void> {
    //remove previous files---
    if (fs.existsSync(this.toReconstructFilePath)) {
      fs.rmSync(this.toReconstructFilePath);
    }

    // if (fs.existsSync(this.outputModelDiffPath)) {
    //   await fs.promises.rm(this.outputModelDiffPath, {
    //     recursive: true,
    //     force: true,
    //   });
    // }
    //---

    this.offFileData = '';
    let prevTimestamp: number | null = null;
    const { sockets } = this.server.sockets;

    for (const row of this.csvData) {
      if (!sockets.has(client.id)) {
        //socket is disconnected
        return;
      }
      if (prevTimestamp) {
        await this.timeout((row.Timestamp - prevTimestamp) * 1000);
      }
      prevTimestamp = row.Timestamp;
      this.server.emit('telemetryData', this.telemetryToDto(row));
    }

    this.server.emit('end');
  }

  @SubscribeMessage('off-file-snippet')
  handleOffFileSnippet(client: Socket, payload: string): void {
    this.offFileData += payload;
  }

  @SubscribeMessage('off-file-completed')
  handleOffFileCompleted(client: Socket, numberOfPoints: number): void {
    // OFF file header
    const header = `NOFF\n${numberOfPoints} 0 0\n`;

    const completeOffFile = header + this.offFileData;
    fs.writeFileSync(this.toReconstructFilePath, completeOffFile);
    this.offFileData = '';
    console.log(
      `OFF file saved to ${this.toReconstructFilePath} with ${numberOfPoints} points`,
    );
  }
}

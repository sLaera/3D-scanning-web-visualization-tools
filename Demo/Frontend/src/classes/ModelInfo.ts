import { Utils } from '@/classes/Utils'

/**
 * Model information that Unity will use to load the gltf
 **/
export default class ModelInfo {
  /**
   * URL of the gltf file.
   * By default, glTFs are loaded via UnityWebRequests.
   * File paths have to be prefixed with file://
   **/
  ModelUrl: string

  /**
   * Position Vector where to generate the model
   **/
  Position: { x: number; y: number; z: number }

  constructor(
    modelUrl: string,
    transform: { x: number; y: number; z: number } = {
      x: 0,
      y: 0,
      z: 0
    }
  ) {
    this.ModelUrl = modelUrl
    this.Position = transform
  }

  /**
   * Create a Json of the class fields
   **/
  toJSON(): string {
    return JSON.stringify({
      ModelUrl: this.ModelUrl,
      Position: this.Position
    })
  }

  /**
   * Set a random x,y,z value to the position of the model.
   * @param min - Minimum random value
   * @param max - Maximum random value
   * @return - The class instance itself
   */
  randomPosition(min: number = 1, max: number = 10): ModelInfo {
    this.Position = {
      x: Utils.getRandomInt(min, max),
      y: Utils.getRandomInt(min, max),
      z: Utils.getRandomInt(min, max)
    }
    return this
  }
}

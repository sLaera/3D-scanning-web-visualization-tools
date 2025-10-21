import type { ModelSelectOption } from '@/types/3dModel'
import type { ApiResponse, ModelDiffDto, ModelDiffInfo, ReconstructDto } from '@/types/api'
import { Utils } from '@/classes/Utils'

export const host = 'http://localhost:3000'

export default class Api {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {},
    isResponseText = false
  ): Promise<ApiResponse<T>> {
    let data: T | null = null
    let error: string | null = null

    try {
      const response = await fetch(`${host}${endpoint}`, options)

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status} - ${response.statusText}`)
      }

      data = isResponseText ? ((await response.text()) as T) : ((await response.json()) as T)
    } catch (e) {
      error = Utils.getErrorMessage(e)
      console.error({ e })
    }

    return { data, error }
  }

  public static getMeshes(): Promise<ApiResponse<ModelSelectOption[]>> {
    return this.request<ModelSelectOption[]>('/meshes')
  }

  public static remesh(dto: ReconstructDto): Promise<ApiResponse<string>> {
    return this.request<string>(
      '/meshes/reconstruct',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json;charset=UTF-8' },
        body: JSON.stringify(dto)
      },
      true
    )
  }

  public static generateDifference(dto: ModelDiffDto): Promise<ApiResponse<ModelDiffInfo>> {
    return this.request<ModelDiffInfo>('/meshes/generate-difference', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json;charset=UTF-8' },
      body: JSON.stringify(dto)
    })
  }
}

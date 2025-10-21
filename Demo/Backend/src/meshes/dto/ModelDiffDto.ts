export default class ModelDiffDto {
  modelName: string;
  positiveBreakpoints: number[];
  negativeBreakpoints: number[];
  recompute: boolean;
}

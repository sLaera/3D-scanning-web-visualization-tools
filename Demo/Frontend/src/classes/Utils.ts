import type { ErrorWithMessage } from '@/types/errors'
import { isErrorWithMessage } from '@/types/errors'

export class Utils {
  static getRandomInt(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min
  }

  private static toErrorWithMessage(maybeError: unknown): ErrorWithMessage {
    if (isErrorWithMessage(maybeError)) return maybeError

    try {
      return new Error(JSON.stringify(maybeError))
    } catch {
      // fallback in case there's an error stringifying the maybeError
      // like with circular references, for example.
      return new Error(String(maybeError))
    }
  }

  /**
   * Will get caught error string
   * @param error
   */
  static getErrorMessage(error: unknown) {
    return this.toErrorWithMessage(error).message
  }

  /**
   * Limit the number of function executions in un periodo di tempo
   * @param fn - function
   * @param limit - number of milliseconds between function executions
   */
  static throttle<T extends (...args: any[]) => void>(fn: T, limit: number) {
    let lastCall = 0;
    return function (this: ThisParameterType<T>, ...args: Parameters<T>) {
      const now = Date.now();
      if (now - lastCall >= limit) {
        lastCall = now;
        fn.apply(this, args);
      }
    };
  }
}

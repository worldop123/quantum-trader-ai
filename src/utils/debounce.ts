/**
 * 防抖函数
 * 在事件被触发n秒后再执行回调，如果在这n秒内又被触发，则重新计时
 * @param fn 要执行的函数
 * @param delay 延迟时间（毫秒）
 * @param immediate 是否立即执行
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300,
  immediate: boolean = false
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null

  return function (this: any, ...args: Parameters<T>) {
    if (timer) {
      clearTimeout(timer)
    }

    if (immediate) {
      // 立即执行
      const callNow = !timer
      timer = setTimeout(() => {
        timer = null
      }, delay)

      if (callNow) {
        fn.apply(this, args)
      }
    } else {
      // 延迟执行
      timer = setTimeout(() => {
        fn.apply(this, args)
        timer = null
      }, delay)
    }
  }
}

/**
 * 节流函数
 * 规定在一个单位时间内，只能触发一次函数。如果这个单位时间内触发多次函数，只有一次生效
 * @param fn 要执行的函数
 * @param delay 间隔时间（毫秒）
 * @param leading 是否在开始时执行
 * @param trailing 是否在结束时执行
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300,
  leading: boolean = true,
  trailing: boolean = true
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  let previous = 0

  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()

    // 如果不希望立即执行
    if (!leading && !previous) {
      previous = now
    }

    const remaining = delay - (now - previous)

    if (remaining <= 0 || remaining > delay) {
      if (timer) {
        clearTimeout(timer)
        timer = null
      }
      previous = now
      fn.apply(this, args)
    } else if (!timer && trailing) {
      timer = setTimeout(() => {
        previous = leading ? Date.now() : 0
        timer = null
        fn.apply(this, args)
      }, remaining)
    }
  }
}

/**
 * 异步函数防抖
 * 适用于返回Promise的函数
 * @param fn 要执行的异步函数
 * @param delay 延迟时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounceAsync<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let timer: ReturnType<typeof setTimeout> | null = null

  return function (this: any, ...args: Parameters<T>): Promise<ReturnType<T>> {
    return new Promise((resolve, reject) => {
      if (timer) {
        clearTimeout(timer)
      }

      timer = setTimeout(() => {
        fn.apply(this, args)
          .then(resolve)
          .catch(reject)
          .finally(() => {
            timer = null
          })
      }, delay)
    })
  }
}

/**
 * 异步函数节流
 * 适用于返回Promise的函数，确保在delay时间内只执行一次
 * @param fn 要执行的异步函数
 * @param delay 间隔时间（毫秒）
 * @returns 节流后的函数
 */
export function throttleAsync<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  let lastCall = 0
  let pendingPromise: Promise<ReturnType<T>> | null = null

  return function (this: any, ...args: Parameters<T>): Promise<ReturnType<T>> {
    const now = Date.now()

    if (now - lastCall >= delay) {
      lastCall = now
      pendingPromise = fn.apply(this, args)
      return pendingPromise
    }

    // 如果在节流时间内，返回上一次的Promise
    if (pendingPromise) {
      return pendingPromise
    }

    // 否则创建一个新的Promise，在delay后执行
    pendingPromise = new Promise((resolve, reject) => {
      setTimeout(() => {
        lastCall = Date.now()
        fn.apply(this, args)
          .then(resolve)
          .catch(reject)
          .finally(() => {
            pendingPromise = null
          })
      }, delay - (now - lastCall))
    })

    return pendingPromise
  }
}

/**
 * 使用示例：
 *
 * // 防抖搜索
 * const search = debounce((keyword: string) => {
 *   // 执行搜索
 *   console.log('search:', keyword)
 * }, 300)
 *
 * // 节流滚动
 * const handleScroll = throttle(() => {
 *   // 处理滚动
 *   console.log('scroll')
 * }, 100)
 *
 * // 异步防抖
 * const fetchData = debounceAsync(async (id: number) => {
 *   const res = await api.getData(id)
 *   return res
 * }, 500)
 */

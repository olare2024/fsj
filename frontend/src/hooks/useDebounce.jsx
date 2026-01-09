// src/hooks/useDebounce.jsx
import { useEffect, useState, useRef, useCallback } from 'react';

/**
 * Custom React hook for debouncing values with TypeScript-like type safety
 * 
 * @template T - The type of the value to debounce
 * @param {T} value - The value to debounce
 * @param {number} delay - Delay in milliseconds (default: 500ms)
 * @param {Object} options - Additional options
 * @param {boolean} options.leading - Execute callback on leading edge (default: false)
 * @param {boolean} options.trailing - Execute callback on trailing edge (default: true)
 * @param {number} options.maxWait - Maximum time callback is allowed to be delayed
 * @returns {T} The debounced value
 * 
 * @example
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearch = useDebounce(searchTerm, 300);
 * 
 * useEffect(() => {
 *   // This will only run 300ms after user stops typing
 *   fetchResults(debouncedSearch);
 * }, [debouncedSearch]);
 */
const useDebounce = (value, delay = 500, options = {}) => {
  const {
    leading = false,
    trailing = true,
    maxWait
  } = options;

  const [debouncedValue, setDebouncedValue] = useState(value);
  const timerRef = useRef(null);
  const maxTimerRef = useRef(null);
  const leadingExecutedRef = useRef(false);
  const valueRef = useRef(value);
  const trailingEdgeRef = useRef(false);

  // Update ref with latest value
  useEffect(() => {
    valueRef.current = value;
  }, [value]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
      if (maxTimerRef.current) {
        clearTimeout(maxTimerRef.current);
      }
    };
  }, []);

  // Main debounce effect
  useEffect(() => {
    // Clear existing timers
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    if (maxTimerRef.current) {
      clearTimeout(maxTimerRef.current);
      maxTimerRef.current = null;
    }

    const executeCallback = () => {
      setDebouncedValue(valueRef.current);
      leadingExecutedRef.current = false;
      trailingEdgeRef.current = false;
    };

    // Leading edge execution
    if (leading && !leadingExecutedRef.current) {
      executeCallback();
      leadingExecutedRef.current = true;
      trailingEdgeRef.current = true;
    }

    // Max wait timer
    if (maxWait && !maxTimerRef.current && trailingEdgeRef.current) {
      maxTimerRef.current = setTimeout(() => {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
          timerRef.current = null;
        }
        executeCallback();
      }, maxWait);
    }

    // Trailing edge execution
    if (trailing) {
      timerRef.current = setTimeout(executeCallback, delay);
    }

    // No cleanup needed here - cleanup happens in unmount effect
  }, [value, delay, leading, trailing, maxWait]);

  return debouncedValue;
};

/**
 * Hook for debouncing callback functions
 * 
 * @template Args - Type of arguments array
 * @param {(...args: Args) => void} callback - Function to debounce
 * @param {number} delay - Delay in milliseconds (default: 500ms)
 * @param {Object} options - Additional options
 * @param {boolean} options.leading - Execute on leading edge (default: false)
 * @param {boolean} options.trailing - Execute on trailing edge (default: true)
 * @returns {(...args: Args) => void} Debounced function
 * 
 * @example
 * const debouncedSearch = useDebouncedCallback(
 *   (searchTerm) => fetchResults(searchTerm),
 *   300
 * );
 * 
 * // Usage
 * <input onChange={(e) => debouncedSearch(e.target.value)} />
 */
export const useDebouncedCallback = (callback, delay = 500, options = {}) => {
  const {
    leading = false,
    trailing = true
  } = options;

  const callbackRef = useRef(callback);
  const timerRef = useRef(null);
  const leadingExecutedRef = useRef(false);

  // Update callback ref
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  const debouncedCallback = useCallback((...args) => {
    // Clear existing timer
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    // Leading execution
    if (leading && !leadingExecutedRef.current) {
      callbackRef.current(...args);
      leadingExecutedRef.current = true;
    }

    // Trailing execution
    if (trailing) {
      timerRef.current = setTimeout(() => {
        if (trailing) {
          callbackRef.current(...args);
        }
        leadingExecutedRef.current = false;
      }, delay);
    }
  }, [delay, leading, trailing]);

  // Cancel pending execution
  const cancel = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    leadingExecutedRef.current = false;
  }, []);

  // Flush pending execution
  const flush = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      callbackRef.current();
      timerRef.current = null;
    }
    leadingExecutedRef.current = false;
  }, []);

  return Object.assign(debouncedCallback, { cancel, flush });
};

/**
 * Hook for throttling values
 * 
 * @template T - Type of the value
 * @param {T} value - The value to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {T} The throttled value
 * 
 * @example
 * const [scrollPosition, setScrollPosition] = useState(0);
 * const throttledScroll = useThrottle(scrollPosition, 100);
 * 
 * window.addEventListener('scroll', () => {
 *   setScrollPosition(window.scrollY);
 * });
 */
export const useThrottle = (value, limit) => {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastRan = useRef(Date.now());

  useEffect(() => {
    const handler = setTimeout(() => {
      if (Date.now() - lastRan.current >= limit) {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }
    }, limit - (Date.now() - lastRan.current));

    return () => {
      clearTimeout(handler);
    };
  }, [value, limit]);

  return throttledValue;
};

/**
 * Hook for throttling callback functions
 * 
 * @template Args - Type of arguments array
 * @param {(...args: Args) => void} callback - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {(...args: Args) => void} Throttled function
 */
export const useThrottledCallback = (callback, limit) => {
  const callbackRef = useRef(callback);
  const lastRanRef = useRef(0);
  const timeoutRef = useRef(null);

  // Update callback ref
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const throttledCallback = useCallback((...args) => {
    const now = Date.now();
    
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // If enough time has passed, execute immediately
    if (now - lastRanRef.current >= limit) {
      callbackRef.current(...args);
      lastRanRef.current = now;
    } else {
      // Schedule execution for remaining time
      timeoutRef.current = setTimeout(() => {
        callbackRef.current(...args);
        lastRanRef.current = Date.now();
      }, limit - (now - lastRanRef.current));
    }
  }, [limit]);

  // Cancel pending execution
  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  // Flush pending execution
  const flush = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      callbackRef.current();
      timeoutRef.current = null;
      lastRanRef.current = Date.now();
    }
  }, []);

  return Object.assign(throttledCallback, { cancel, flush });
};

/**
 * Enhanced debounce hook with immediate callback execution capability
 * 
 * @template T - Type of the value
 * @param {T} value - The value to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {[T, () => void, () => void]} [debouncedValue, cancel, flush]
 */
export const useEnhancedDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  const timerRef = useRef(null);
  const valueRef = useRef(value);

  // Update ref with latest value
  useEffect(() => {
    valueRef.current = value;
  }, [value]);

  useEffect(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      setDebouncedValue(valueRef.current);
    }, delay);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [value, delay]);

  const cancel = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const flush = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      setDebouncedValue(valueRef.current);
      timerRef.current = null;
    }
  }, []);

  return [debouncedValue, cancel, flush];
};

/**
 * Hook for sequential debouncing (useful for API calls)
 * 
 * @template T - Type of the value
 * @param {T} value - The value to debounce
 * @param {number} delay - Delay in milliseconds
 * @param {() => Promise<void> | void} callback - Async callback to execute
 * @returns {T} The debounced value
 */
export const useAsyncDebounce = (value, delay, callback) => {
  const timerRef = useRef(null);

  useEffect(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(async () => {
      if (callback) {
        try {
          await callback(value);
        } catch (error) {
          console.error('Async debounce error:', error);
        }
      }
    }, delay);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [value, delay, callback]);

  return value;
};

// Default export
export default useDebounce;

// Utility functions
export const debounce = (func, delay) => {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};
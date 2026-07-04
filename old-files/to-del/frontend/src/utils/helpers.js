/**
 * A collection of utility functions for the application.
 */

/**
 * Converts a file size in bytes to a human-readable string (KB, MB, GB, etc.).
 *
 * @param {number} bytes - The file size in bytes.
 * @param {number} [decimals=2] - The number of decimal places to display.
 * @returns {string} A formatted string representing the file size.
 */
export const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
  
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
    const i = Math.floor(Math.log(bytes) / Math.log(k));
  
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };
  
  /**
   * Truncates a string to a specified maximum length and appends an ellipsis.
   *
   * @param {string} text - The string to truncate.
   * @param {number} [maxLength=50] - The maximum length of the string before truncation.
   * @returns {string} The truncated string with an ellipsis, or the original string if it's shorter than maxLength.
   */
  export const truncateText = (text, maxLength = 50) => {
    if (typeof text !== 'string' || text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  };
  
  /**
   * Generates a simple, non-secure unique ID for client-side use (e.g., list keys).
   *
   * @returns {string} A short, random string.
   */
  export const generateClientSideId = () => {
    return Math.random().toString(36).substring(2, 9);
  };
  
  
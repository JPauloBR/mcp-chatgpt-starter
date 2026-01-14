// Image resolver for ChatGPT widget compatibility
// Imports base64-inlined images and provides a resolver function

import {
  ipad_air_13,
  samsung_tab_s9,
} from "./images.generated.js";

// Also import shared images from carousel (these devices appear in both widgets)
import {
  iphone_17_pro_max,
  samsung_s25_ultra,
  iphone_15_pro_max,
  google_pixel_9a,
  samsung_fold_6,
  iphone_15,
  ipad_pro_13,
  iphone_14,
} from "../att-products-carousel/images.generated.js";

// Map image paths to base64 data URLs
const imageMap = {
  "./images/iphone-17-pro-max.png": iphone_17_pro_max,
  "./images/samsung-s25-ultra.png": samsung_s25_ultra,
  "./images/iphone-15-pro-max.png": iphone_15_pro_max,
  "./images/google-pixel-9a.png": google_pixel_9a,
  "./images/samsung-fold-6.png": samsung_fold_6,
  "./images/iphone-15.png": iphone_15,
  "./images/ipad-pro-13.png": ipad_pro_13,
  "./images/iphone-14.png": iphone_14,
  "./images/ipad-air-13.png": ipad_air_13,
  "./images/samsung-tab-s9.png": samsung_tab_s9,
};

export const resolveImage = (path) => imageMap[path] || path;

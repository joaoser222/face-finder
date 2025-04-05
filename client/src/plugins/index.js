/**
 * plugins/index.js
 *
 * Automatically included in `./src/main.js`
 */

// Plugins
import vuetify from './vuetify'
import router from '@/router'
import { vMaska } from "maska/vue";

export function registerPlugins (app) {
  app.directive('maska',vMaska);
  app
    .use(vuetify)
    .use(router)
}

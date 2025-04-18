/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// Tabler icons
import * as TablerIcons from '@tabler/icons-vue'

import { h } from 'vue'
import { VCardActions } from 'vuetify/components'

const tablerIcons = {}
for (const name in TablerIcons) {
  tablerIcons[name.replace(/^Icon/, '')] = TablerIcons[name]
}

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'light',
  },
  defaults: {
    global: {
      elevation: 0,
    },
    VCard: {
      rounded: 'lg'
    },
    VTextField: {
      rounded: 'lg',
      variant: 'outlined',
      density: 'comfortable',
      clearIcon: 'X',
      clearable: true
    },
    VTextarea: {
      rounded: 'lg',
      variant: 'outlined',
    },
    VBtn: {
      rounded: 'lg',
      variant: 'flat'
    },
    VChip: {
      rounded: 'lg',
    },
    VFileInput: {
      prependIcon: null,
      rounded: 'lg',
      variant: 'outlined',
      density: 'comfortable',
      clearIcon: 'X',
      clearable: true
    },
    VAutocomplete: {
      rounded: 'lg',
      variant: 'outlined',
      density: 'comfortable',
      clearIcon: 'X',
      clearable: true
    },
    VListItem: {
      rounded: 'lg',
    },
    VDialog: {
      VProgressCircular:{
        size: '90',
        color: 'primary',
        indeterminate: true
      }
    },
    VCheckbox: {
      trueIcon: 'SquareCheckFilled',
      falseIcon: 'Square',
      variant: 'flat'
    }
  },
  icons: {
    defaultSet: 'tabler',
    sets: {
      tabler: {
        component: (props) => {
          const { icon } = props
          return h(tablerIcons[icon])
        },
      },
    },
  },
})

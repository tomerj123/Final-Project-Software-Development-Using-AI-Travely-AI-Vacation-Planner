import { createTheme } from '@mui/material';
import { PaletteOptions } from '@mui/material/styles/createPalette';
import { CustomFontFamily, getFontName } from './CustomFonts';

// change the theme like you want
export const lightTheme = createTheme({
    palette: {
        mode: 'light',
        background: {
            default: '#F5F5F7',
        },
        info: {
            main: '#767676',
        },
        low: {
            main: '#D76B66',
        },
        medium: {
            main: '#F6CF7D',
        },
        high: {
            main: '#3c6ed4',
        },
        critical: {
            main: '#660000',
        },
        black: {
            main: '#000000',
        },
        red: {
            main: '#D76B66',
        },
        green: {
            main: '#75C57F',
        },
        blue: {
            main: '#73ACEF',
        },
        // Customize other palette colors as needed
    } as PaletteOptions,
    typography: {
        fontFamily: getFontName(CustomFontFamily.inter).regular,
        h5: {
            fontFamily: getFontName(CustomFontFamily.inter).bold,
        },
        h6: {
            fontFamily: getFontName(CustomFontFamily.inter).bold,
        },
        subtitle1: {
            fontFamily: getFontName(CustomFontFamily.inter).bold,
        },
        // Customize typography as needed
    },
    components: {
        MuiListItemText: {
            styleOverrides: {
                primary: {
                    color: 'rgba(0, 0, 0, 0.87)',
                },
            },
        },
        MuiInputBase: {
            styleOverrides: {
                sizeSmall: {
                    paddingTop: '3px',
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                },
            },
        },
        MuiTextField: {
            defaultProps: {
                variant: 'outlined',
                size: 'small',
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundColor: 'white',
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundColor: 'white',
                },
            },
        },
        // Customize other component configurations as needed
    },
    shadows: createTheme().shadows, // Customize shadow options
    shape: {
        borderRadius: 8, // Customize border radius
    },
    breakpoints: {
        values: {
            ...createTheme().breakpoints.values,
            xs: 0,
            sm: 600,
            md: 960,
            lg: 1280,
            xl: 1920,
        },
    },
    transitions: {
        easing: {
            easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        },
        duration: {
            shortest: 150,
            shorter: 200,
            short: 250,
            standard: 300,
            complex: 375,
            enteringScreen: 225,
            leavingScreen: 195,
        },
    },
    zIndex: {
        appBar: 1200,
        drawer: 1100,
    },
    // Customize other theme configurations as needed
});

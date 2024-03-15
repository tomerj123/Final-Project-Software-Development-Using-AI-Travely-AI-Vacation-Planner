import { CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import { SomeScreen2 } from './screens/some-screen-2/SomeScreen2';
import { darkTheme } from './theme/DarkTheme';
import { lightTheme } from './theme/LightTheme';
import { MainPage } from './screens/main-page/MainPage';

const App = () => {
    const darkMode = false;
    return (
        <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
            <CssBaseline />
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<MainPage someProps={77777} />} />
                    <Route path="/some-screen2" element={<SomeScreen2 someProps={7777777} />} />

                    {/* Handle 404 - Not Found */}
                    <Route path="*" element={<div>404 - Not Found</div>} />
                </Routes>
            </BrowserRouter>
        </ThemeProvider>
    );
};

export default App;

import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import HomePage from './pages/HomePage';
import ExplorePage from './pages/ExplorePage';
import { CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const appBarRef = useRef(null);
  const [headerHeight, setHeaderHeight] = useState(0);

  useEffect(() => {
    if (appBarRef.current) {
      setHeaderHeight(appBarRef.current.offsetHeight);
    }
  }, [appBarRef.current]); // Recalculate if ref changes (e.g., on mount)

  // Also listen for window resize to update header height if it's responsive
  useEffect(() => {
    const handleResize = () => {
      if (appBarRef.current) {
        setHeaderHeight(appBarRef.current.offsetHeight);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppBar ref={appBarRef} position="static">
          <Toolbar>
            <NavBar /> {/* NavBar content is now inside AppBar/Toolbar */}
          </Toolbar>
        </AppBar>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/explore" element={<ExplorePage headerHeight={headerHeight} />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;

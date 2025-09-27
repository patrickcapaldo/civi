// This file is part of the CIVI project.
// It is subject to the Polyform Noncommercial License 1.0.0.
// See the LICENSE file in the root of this project for the full license text.

import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import HomePage from './pages/HomePage';
import ExplorePage from './pages/ExplorePage';
import AnalysePage from './pages/AnalysePage'; // New import
import CaseStudiesPage from './pages/CaseStudies/CaseStudiesPage';
import CaseStudyArticle from './pages/CaseStudies/CaseStudyArticle';
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
  }, []); // Recalculate on mount

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
      <Router basename="/">
        <AppBar ref={appBarRef} position="fixed">
          <Toolbar>
            <NavBar /> {/* NavBar content is now inside AppBar/Toolbar */}
          </Toolbar>
        </AppBar>
        <div style={{ paddingTop: `${headerHeight}px` }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/explore" element={<ExplorePage headerHeight={headerHeight} />} />
            <Route path="/analyse" element={<AnalysePage headerHeight={headerHeight} />} /> {/* New route */}
            <Route path="/case-studies" element={<CaseStudiesPage headerHeight={headerHeight} />} />
            <Route path="/case-studies/:slug" element={<CaseStudyArticle headerHeight={headerHeight} />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;

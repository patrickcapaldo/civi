import React from 'react';
import { Link } from 'react-router-dom';
import { Typography, Button } from '@mui/material';

const NavBar = () => {
  return (
    <>
      <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
        CIVI
      </Typography>
      <Button color="inherit" component={Link} to="/">Home</Button>
      <Button color="inherit" component={Link} to="/explore">Explore</Button>
      <Button color="inherit" component={Link} to="/analyse">Analyse</Button> {/* New button */}
    </>
  );
};

export default NavBar;
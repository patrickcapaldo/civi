import React, { useState, useEffect } from 'react';
import { Grid, TextField, FormControl, InputLabel, Select, MenuItem, Box, InputAdornment, IconButton, Paper, Button } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const FilterBar = ({ availableTags, filters, onFilterChange }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [countrySearchTerm, setCountrySearchTerm] = useState('');
    const [showCountrySuggestions, setShowCountrySuggestions] = useState(false);

    // Effect to clear country search term if all countries are deselected externally
    useEffect(() => {
        if (filters.countries.length === 0) {
            setCountrySearchTerm('');
        }
    }, [filters.countries]);

    const handleMultiSelectChange = (name, newValue) => {
        onFilterChange(name, newValue);
    };

    const handleSearchSubmit = () => {
        if (searchTerm.trim() !== '') {
            onFilterChange('search', searchTerm.trim());
            setSearchTerm(''); // Clear search bar after submission
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            handleSearchSubmit();
        }
    };

    const handleCountryInputChange = (event) => {
        setCountrySearchTerm(event.target.value);
        setShowCountrySuggestions(true);
    };

    const handleCountrySelect = (country) => {
        // Only add if not already selected
        if (!filters.countries.includes(country)) {
            const newCountries = [...filters.countries, country];
            onFilterChange('countries', newCountries);
        }
        setCountrySearchTerm(''); // Clear input after selection
        setShowCountrySuggestions(false);
    };

    const filteredCountrySuggestions = availableTags.countries.filter(country =>
        country.toLowerCase().includes(countrySearchTerm.toLowerCase())
    );

    return (
        <Box sx={{ mb: 4, p: 2, border: '1px solid #444', borderRadius: 1 }}>
            <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        label="Search for keyword(s)..."
                        name="search"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyDown={handleKeyDown}
                        InputProps={{
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton onClick={handleSearchSubmit} edge="end">
                                        <SearchIcon />
                                    </IconButton>
                                </InputAdornment>
                            ),
                        }}
                    />
                </Grid>
                <Grid item xs={12} sm={4} md={2.6} sx={{ position: 'relative' }}>
                    <TextField
                        fullWidth
                        variant="outlined"
                        label="Country"
                        value={countrySearchTerm}
                        onChange={handleCountryInputChange}
                        onFocus={() => setShowCountrySuggestions(true)}
                        onBlur={() => setTimeout(() => setShowCountrySuggestions(false), 100)} // Delay to allow click on suggestion
                    />
                    {showCountrySuggestions && countrySearchTerm && filteredCountrySuggestions.length > 0 && (
                        <Paper 
                            sx={{
                                position: 'absolute',
                                top: '100%',
                                left: 0,
                                right: 0,
                                zIndex: 1000,
                                maxHeight: 200,
                                overflowY: 'auto',
                                mt: 0.5,
                                bgcolor: '#3a3a3a', // Match analyse-input-text background
                                border: '1px solid #555', // Match analyse-input-text border
                            }}
                        >
                            {filteredCountrySuggestions.map((country) => (
                                <Button
                                    key={country}
                                    onClick={() => handleCountrySelect(country)}
                                    sx={{
                                        display: 'block',
                                        width: '100%',
                                        textAlign: 'left',
                                        color: 'white',
                                        justifyContent: 'flex-start',
                                        textTransform: 'none',
                                        '&:hover': { bgcolor: '#555' },
                                    }}
                                >
                                    {country}
                                </Button>
                            ))}
                        </Paper>
                    )}
                </Grid>
                <Grid item xs={12} sm={4} md={2.6}>
                    <FormControl fullWidth>
                        <InputLabel>Industries</InputLabel>
                        <Select
                            multiple
                            name="industries"
                            value={filters.industries || []}
                            label="Industries"
                            onChange={(e) => handleMultiSelectChange('industries', e.target.value)}
                        >
                            {availableTags.industries?.map(i => <MenuItem key={i} value={i}>{i}</MenuItem>)}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={12} sm={4} md={2.6}>
                    <FormControl fullWidth>
                        <InputLabel>Pillars</InputLabel>
                        <Select
                            multiple
                            name="pillars"
                            value={filters.pillars || []}
                            label="Pillars"
                            onChange={(e) => handleMultiSelectChange('pillars', e.target.value)}
                        >
                            {availableTags.pillars?.map(p => <MenuItem key={p} value={p}>{p}</MenuItem>)}
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>
        </Box>
    );
};

export default FilterBar;
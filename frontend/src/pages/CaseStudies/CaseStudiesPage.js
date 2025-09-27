import React, { useState, useEffect, useMemo } from 'react';
import { Container, Grid, Typography, CircularProgress, Box } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import CaseStudyTile from './CaseStudyTile';
import FilterBar from './FilterBar';
import Pagination from './Pagination';
import ActiveFilters from './ActiveFilters';
import './CaseStudies.css';

const PAGE_SIZE = 9;

const CaseStudiesPage = ({ headerHeight }) => {
    const [allStudies, setAllStudies] = useState([]);
    const [availableTags, setAvailableTags] = useState({ countries: [], industries: [], pillars: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchIndex = async () => {
            try {
                const response = await fetch(`/case-studies/index.json`);
                if (!response.ok) {
                    throw new Error('Could not fetch case studies index.');
                }
                const data = await response.json();
                setAllStudies(data.studies || []);
                setAvailableTags(data.available_tags || {});
            } catch (e) {
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };
        fetchIndex();
    }, []);

    const { filters, page } = useMemo(() => {
        const params = new URLSearchParams(location.search);
        const page = parseInt(params.get('page'), 10) || 1;
        const filters = {
            search: params.get('search') || '',
            countries: params.getAll('country'),
            industries: params.getAll('industry'),
            pillars: params.getAll('pillar'),
        };
        return { filters, page };
    }, [location.search]);

    const filteredStudies = useMemo(() => {
        return allStudies.filter(study => {
            const { search, countries, industries, pillars } = filters;

            const searchKeywords = search.toLowerCase().split(' ').filter(Boolean);
            if (searchKeywords.length > 0 && !searchKeywords.every(kw => study.title.toLowerCase().includes(kw))) {
                return false;
            }

            if (countries.length > 0 && !countries.some(c => study.tags.countries?.includes(c))) {
                return false;
            }
            if (industries.length > 0 && !industries.some(i => study.tags.industries?.includes(i))) {
                return false;
            }
            if (pillars.length > 0 && !pillars.some(p => study.tags.pillars?.includes(p))) {
                return false;
            }

            return true;
        });
    }, [allStudies, filters]);

    const { paginatedStudies, totalPages } = useMemo(() => {
        const totalPages = Math.ceil(filteredStudies.length / PAGE_SIZE);
        const start = (page - 1) * PAGE_SIZE;
        const end = start + PAGE_SIZE;
        return {
            paginatedStudies: filteredStudies.slice(start, end),
            totalPages: totalPages,
        };
    }, [filteredStudies, page]);

    const handleFilterChange = (name, value) => {
        const params = new URLSearchParams(location.search);

        if (name === 'search') {
            if (value) {
                params.set('search', value);
            } else {
                params.delete('search');
            }
        } else {
            // Plural names like 'countries', 'industries', 'pillars'
            let singularName;
            switch (name) {
                case 'countries': singularName = 'country'; break;
                case 'industries': singularName = 'industry'; break;
                case 'pillars': singularName = 'pillar'; break;
                default: return; // Should not happen
            }
            
            params.delete(singularName);
            if (Array.isArray(value)) {
                value.forEach(v => params.append(singularName, v));
            }
        }

        params.set('page', '1');
        navigate(`?${params.toString()}`);
    };

    const handleRemoveFilter = (type, valueToRemove) => {
        if (type === 'search') {
            handleFilterChange('search', '');
        } else {
            const currentValues = filters[type];
            const newValues = currentValues.filter(v => v !== valueToRemove);
            handleFilterChange(type, newValues);
        }
    };

    const handlePageChange = (newPage) => {
        const params = new URLSearchParams(location.search);
        params.set('page', newPage.toString());
        navigate(`?${params.toString()}`);
    };

    if (loading) {
        return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
    }

    if (error) {
        return <Typography color="error" sx={{ mt: 4, textAlign: 'center' }}>Error: {error}</Typography>;
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom>
                Case Studies
            </Typography>
            <Typography variant="body1" paragraph>
                Explore in-depth articles and insights drawing from CIVI data to understand key trends and country-specific analyses.
            </Typography>
            <FilterBar 
                availableTags={availableTags} 
                filters={filters} 
                onFilterChange={handleFilterChange} 
            />
            <ActiveFilters 
                filters={filters} 
                onRemoveFilter={handleRemoveFilter} 
            />
            <Grid container spacing={3} sx={{ mt: 2 }}>
                {paginatedStudies.length > 0 ? (
                    paginatedStudies.map(study => <CaseStudyTile key={study.slug} study={study} />)
                ) : (
                    <Typography sx={{ ml: 3 }}>No case studies found.</Typography>
                )}
            </Grid>
            <Pagination 
                totalPages={totalPages}
                page={page}
                onPageChange={handlePageChange}
            />
        </Container>
    );
};

export default CaseStudiesPage;
import React from 'react';
import PropTypes from 'prop-types';

/* material-ui includes */
import { styled } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses }  from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import TableSortLabel from '@mui/material/TableSortLabel';
import { visuallyHidden } from '@mui/utils';

import NoAssetsFound from './alerts/NoAssetsFound';
import LoadingAssets from './alerts/LoadingAssets';
import {
    formatDay, getAssets, getAssetType, getAssetUrl, getTerms
} from './utils';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
        backgroundColor: '#cacbcc',
        color: theme.palette.common.black,
        fontSize: 16,
        fontWeight: 'bold',
        paddingLeft: '8px',
        paddingRight: '8px',
    }
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
    '&:nth-of-type(odd)': {
        backgroundColor: theme.palette.action.hover,
    },
    // hide last border
    '&:last-child td, &:last-child th': {
        border: 1,
        margin: 1
    }
}));

const headCells = [
    {
        id: 'title',
        label: 'Title',
        sortable: true
    },
    {
        id: 'selections',
        label: 'Selections',
        sortable: false
    },
    {
        id: 'tags',
        label: 'Tags',
        sortable: false
    },
    {
        id: 'vocabulary',
        label: 'Course Vocabulary',
        sortable: false
    },
    {
        id: 'media',
        label: 'Media',
        sortable: false
    },
    {
        id: 'owner',
        label: 'Owner',
        sortable: true
    },
    {
        id: 'date',
        label: 'Date',
        sortable: true
    },
];

function EnhancedTableHead(props) {
    const {order, orderBy, onRequestSort } =
      props;
    const createSortHandler = (property) => (event) => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                {headCells.map((headCell) => (
                    <StyledTableCell
                        key={headCell.id}
                        align="left"
                        padding="none"
                        sortDirection={
                            headCell.sortable && orderBy === headCell.id ?
                                order :
                                false}>
                        {headCell.sortable && (
                            <TableSortLabel
                                active={orderBy === headCell.id}
                                direction={
                                    orderBy === headCell.id ?
                                        order : 'asc'}
                                onClick={createSortHandler(headCell.id)}>
                                {headCell.label}
                                {orderBy === headCell.id ? (
                                    <Box
                                        component="span"
                                        sx={visuallyHidden}>
                                        {
                                            order === 'desc' ?
                                                'sorted descending' :
                                                'sorted ascending'}
                                    </Box>
                                ) : null}
                            </TableSortLabel>
                        )}
                        {!headCell.sortable && (
                            <span>{headCell.label}</span>
                        )}
                    </StyledTableCell>
                ))}
            </TableRow>
        </TableHead>
    );
}

EnhancedTableHead.propTypes = {
    onRequestSort: PropTypes.func.isRequired,
    order: PropTypes.oneOf(['asc', 'desc']).isRequired,
    orderBy: PropTypes.string.isRequired
};

const makeRow = function(data, idx) {
    console.log('makeRow', data);
    return (
        <StyledTableRow
            tabIndex={-1}
            key={idx}>
            <TableCell
                component="th"
                id={`enhanced-table-checkbox-${idx}`}
                scope="row" >
                {data.title}
            </TableCell>
            <TableCell align="left">
                {data.selections}
            </TableCell>
            <TableCell align="left">
                {data.tags}
            </TableCell>
            <TableCell align="left">
                {data.vocabulary}
            </TableCell>
            <TableCell align="left">
                {data.media}
            </TableCell>
            <TableCell align="left">
                {data.owner}
            </TableCell>
            <TableCell align="left">
                {data.date}
            </TableCell>
        </StyledTableRow>
    );
};

export default class CollectionListView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            order: 'asc',
            orderBy: 'title',
        };
        this.handleRequestSort = this.handleRequestSort.bind(this);
        this.handleSort = this.handleSort.bind(this);
    }
    handleRequestSort(event, property) {
        const isAsc =
                this.state.orderBy === property && this.state.order === 'asc';
        this.setState({
            order: isAsc ? 'desc' : 'asc',
            orderBy: property
        });
    }

    handleSort(sortBy, sortDirection) {
        console.log('handleSort', sortBy, sortDirection);
        //this.setState({isLoading: true});

        let sortField = sortBy;
        if (sortField === 'owner') {
            sortField = 'author';
        } else if (sortField === 'date') {
            sortField = 'added';
        }

        const orderBy = sortDirection === 'asc' ? sortField : '-' + sortField;

        const me = this;
        return getAssets(
            this.props.title, this.props.owner, this.props.tags,
            this.props.terms, this.props.date,
            0, orderBy
        ).then(function(d) {
            me.props.onUpdateAssets(d.assets, d.asset_count);
            //me.setState({isLoading: false});
        });
    }

    render() {
        if (this.props.assets.length === 0) {
            return <NoAssetsFound />;
        } else if (this.state.isLoading) {
            return <LoadingAssets />;
        }

        const me = this;

        const rows = [];
        me.props.assets.forEach((asset, idx) => {
            let title = (
                <a
                    href={getAssetUrl(asset.id)}
                    key={idx}
                    onClick={(e) => me.props.enterAssetDetailView(e, asset)}>
                    {asset.title}
                </a>
            );

            let selections = asset.annotation_count;
            let tags = asset.tags.join(', ');
            let media = getAssetType(asset.primary_type);
            let owner = asset.author.public_name;
            let date = formatDay(asset);
            let vocabulary = getTerms(asset.annotations).join(', ');

            rows.push({
                title: title,
                selections: selections,
                tags: tags,
                vocabulary: vocabulary,
                media: media,
                owner: owner,
                date: date
            });
        });

        console.log('rows', rows);
        const renderedRows = rows.map((row, idx) => {
            return makeRow(row, idx);
        });
        console.log('renderedRows', renderedRows);

        return (
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <EnhancedTableHead
                        order={this.state.order}
                        orderBy={this.state.orderBy}
                        onRequestSort={this.handleRequestSort}
                    />
                    <TableBody>
                        {renderedRows}
                    </TableBody>
                </Table>
            </TableContainer>
        );
    }
}

CollectionListView.propTypes = {
    assets: PropTypes.array,
    enterAssetDetailView: PropTypes.func.isRequired,
    onUpdateAssets: PropTypes.func.isRequired,

    // Filters
    owner: PropTypes.string,
    title: PropTypes.string,
    tags: PropTypes.array,
    terms: PropTypes.array,
    date: PropTypes.string
};

import React from 'react';
import PropTypes from 'prop-types';
import { styled } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses }  from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import NoAssetsFound from './alerts/NoAssetsFound';
import {
    formatDay, getAssetType, getAssetUrl, getTerms
} from './utils';
import Box from '@mui/material/Box';
import TableSortLabel from '@mui/material/TableSortLabel';
import { visuallyHidden } from '@mui/utils';

function createData(title, selections, tags, vocabulary, media, owner, date) {
    return { title, selections, tags, vocabulary, media, owner, date };
}

const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
        backgroundColor: '#cacbcc',
        color: theme.palette.common.black,
        fontSize: 16
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

function descendingComparator(a, b, orderBy) {
    if(orderBy === 'title') {
        if (b[orderBy].props.children < a[orderBy].props.children) {
            return -1;
        }
        if (b[orderBy].props.children > a[orderBy].props.children) {
            return 1;
        }
    } else {
        if (b[orderBy] < a[orderBy]) {
            return -1;
        }
        if (b[orderBy] > a[orderBy]) {
            return 1;
        }
        return 0;
    }
}

function getComparator(order, orderBy) {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}


const headCells = [
    {
        id: 'title',
        disablePadding: false,
        label: 'Title',
    },
    {
        id: 'selections',
        disablePadding: true,
        label: 'Selections',
    },
    {
        id: 'tags',
        disablePadding: false,
        label: 'Tags',
    },
    {
        id: 'vocabulary',
        disablePadding: true,
        label: 'Course Vocabulary',
    },
    {
        id: 'media',
        disablePadding: false,
        label: 'Media',
    },
    {
        id: 'owner',
        disablePadding: false,
        label: 'Owner',
    },
    {
        id: 'date',
        disablePadding: false,
        label: 'Date',
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
                        padding={headCell.disablePadding ? 'none' : 'normal'}
                        sortDirection={orderBy === headCell.id ? order : false}
                    >
                        <TableSortLabel
                            active={orderBy === headCell.id}
                            direction={orderBy === headCell.id ? order : 'asc'}
                            onClick={createSortHandler(headCell.id)}
                        >
                            {headCell.label}
                            {orderBy === headCell.id ? (
                                <Box component="span" sx={visuallyHidden}>
                                    {order === 'desc' ?
                                        'sorted descending' :
                                        'sorted ascending'}
                                </Box>
                            ) : null}
                        </TableSortLabel>
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

export default class CollectionListView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: false,
            order: 'asc',
            orderBy: 'title',
        };
        this.handleRequestSort = this.handleRequestSort.bind(this);
    }
    handleRequestSort(event, property) {
        const isAsc =
                this.state.orderBy === property && this.state.order === 'asc';
        this.setState({
            order: isAsc ? 'desc' : 'asc',
            orderBy: property
        });
    }

    render() {
        if (this.props.assets.length === 0) {
            return <NoAssetsFound />;
        }

        const me = this;

        const rows = [];
        me.props.assets.map((asset, index) => {
            let title = <a
                href={getAssetUrl(asset.id)}
                key={index}
                onClick={(e) => me.props.enterAssetDetailView(e, asset)}>
                {asset.title}
            </a>;
            let selections = asset.annotation_count;
            let tags = asset.tags.join(', ');
            let media = getAssetType(asset.primary_type);
            let owner = asset.author.public_name;
            let date = formatDay(asset);
            let vocabulary = getTerms(asset.annotations).join(', ');
            rows.push(createData(
                title, selections, tags, vocabulary, media, owner, date));
        });

        return (
            <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <EnhancedTableHead
                        order={this.state.order}
                        orderBy={this.state.orderBy}
                        onRequestSort={this.handleRequestSort}
                    />
                    <TableBody>
                        {rows.slice().sort(getComparator(
                            this.state.order, this.state.orderBy))
                            .map((row, index) => {
                                const labelId =
                                `enhanced-table-checkbox-${index}`;
                                return (
                                    <StyledTableRow
                                        tabIndex={-1}
                                        key={index} >
                                        <TableCell
                                            component="th"
                                            id={labelId}
                                            scope="row" >
                                            {row.title}
                                        </TableCell>
                                        <TableCell align="left">
                                            {row.selections}
                                        </TableCell>
                                        <TableCell align="left">
                                            {row.tags}
                                        </TableCell>
                                        <TableCell align="left">
                                            {row.vocabulary}
                                        </TableCell>
                                        <TableCell align="left">
                                            {row.media}
                                        </TableCell>
                                        <TableCell align="left">
                                            {row.owner}
                                        </TableCell>
                                        <TableCell align="left">
                                            {row.date}
                                        </TableCell>
                                    </StyledTableRow>
                                );
                            })
                        }
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

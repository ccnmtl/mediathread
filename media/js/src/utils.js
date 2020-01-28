import Cookies from 'js-cookie';

/**
 * A wrapper for `fetch` that passes along auth credentials.
 */
const authedFetch = function(url, method = 'get', data = null) {
    const token = Cookies.get('csrftoken');
    return fetch(url, {
        method: method,
        headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': token
        },
        body: data,
        credentials: 'same-origin'
    });
};

const getAssetData = function() {
    return authedFetch('/api/asset/?annotations=true')
        .then(function(response) {
            if (response.status === 200) {
                return response.json();
            } else {
                throw 'Error loading assets: ' +
                    `(${response.status}) ${response.statusText}`;
            }
        });
};

const isSameDay = function(d1, d2) {
    return d1.getDate() === d2.getDate() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getFullYear() === d2.getFullYear();
};

/**
 * Filter an asset-like object based on the given filters.
 *
 * obj can be an asset or an asset annotation.
 *
 * Returns obj if it passes the filters, otherwise null.
 */
const filterObj = function(obj, filters) {
    // Filter out non-matching titles
    if (
        filters.title && (
            obj.title.toLowerCase().indexOf(
                filters.title
            ) === -1)
    ) {
        return null;
    }

    // Filter out non-matching owners
    if (
        filters.owner &&
            filters.owner !== 'all' &&
            filters.owner !== obj.author.username
    ) {
        return null;
    }

    // Filter out non-matching tags
    if (filters.tags) {
        // TODO
    }

    // Filter out non-matching dates
    if (
        filters.date &&
            filters.date !== 'all'
    ) {
        const modified = obj.modified || obj.metadata.modified;
        const modifiedDate = new Date(modified);

        let filterDate = new Date();
        if (filters.date === 'today') {
            if (!isSameDay(filterDate, modifiedDate)) {
                return null;
            }
        } else if (filters.date === 'yesterday') {
            filterDate.setDate(filterDate.getDate() - 1);
            if (!isSameDay(filterDate, modifiedDate)) {
                return null;
            }
        } else if (filters.date === 'within-last-week') {
            filterDate.setDate(filterDate.getDate() - 7);
            if (modifiedDate < filterDate) {
                return null;
            }
        }
    }

    return obj;
};

export {getAssetData, filterObj};

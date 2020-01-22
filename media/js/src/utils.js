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
    return d1.getDay() === d2.getDay() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getYear() === d2.getYear();
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

    // Filter out non-matching dates
    if (
        filters.date &&
            filters.date !== 'all'
    ) {
        const modified = obj.modified || obj.metadata.modified;
        const modifiedDate = new Date(modified);

        let filterDate;
        if (filters.date === 'today') {
            filterDate = new Date();
            if (!isSameDay(filterDate, modifiedDate)) {
                return null;
            }
        }
    }

    return obj;
};

export {getAssetData, filterObj};

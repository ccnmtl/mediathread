/* eslint-env jest, node */
import fs from 'fs';
import React from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { act } from 'react-dom/test-utils';
import AssetFilter from './AssetFilter';

let container = null;
beforeEach(() => {
    // setup a DOM element as a render target
    container = document.createElement('div');
    document.body.appendChild(container);
});

afterEach(() => {
    // cleanup on exiting
    unmountComponentAtNode(container);
    container.remove();
    container = null;
});

it('renders the asset filter', async() => {
    const assetData = fs.readFileSync('media/js/test/asset-fixture.json');
    const fakeAssets = [JSON.parse(assetData)];

    jest.spyOn(global, 'fetch').mockImplementation(
        () => Promise.resolve({
            json: () => Promise.resolve(fakeAssets)
        })
    );

    // Use the asynchronous version of act to apply resolved promises
    await act(async() => {
        render(
            <AssetFilter
                assets={fakeAssets}
                tags={[]}
                terms={[]}
                viewMode="grid"
                hidePagination={false}
                onUpdateItems={function() {}}
                onUpdateFilter={function() {}}
                setViewMode={function() {}}
                onClearFilter={function() {}}
            />,
            container
        );
    });

    expect(container.textContent).toContain('Search');

    // remove the mock to ensure tests are completely isolated
    global.fetch.mockRestore();
});

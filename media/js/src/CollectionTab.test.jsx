/* eslint-env jest, node */
import fs from 'fs';
import React from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { act } from 'react-dom/test-utils';
import CollectionTab from './CollectionTab';

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

const fakeUser = {
    id: 12,
    name: 'Test User'
};
const assetData = fs.readFileSync('media/js/test/asset-fixture.json');
const fakeAsset = JSON.parse(assetData);

it('renders the collection tab grid layout', async() => {
    jest.spyOn(global, 'fetch').mockImplementation(
        () => Promise.resolve({
            json: () => Promise.resolve(fakeAsset)
        })
    );

    // Use the asynchronous version of act to apply resolved promises
    await act(async() => {
        render(
            <CollectionTab
                currentUser={fakeUser.id}
                onUpdateAssets={function() {}}
                assets={[fakeAsset]} />,
            container
        );
    });

    expect(container.textContent).toContain(fakeAsset.title);
    expect(container.textContent).toContain('Previous');
    expect(container.textContent).toContain('Next');

    // remove the mock to ensure tests are completely isolated
    global.fetch.mockRestore();
});

it('renders the collection tab list layout', async() => {
    jest.spyOn(global, 'fetch').mockImplementation(
        () => Promise.resolve({
            json: () => Promise.resolve(fakeAsset)
        })
    );

    // Use the asynchronous version of act to apply resolved promises
    await act(async() => {
        render(
            <CollectionTab
                currentUser={fakeUser.id}
                onUpdateAssets={function() {}}
                assets={[fakeAsset]} />,
            container
        );
    });

    const button = document.querySelector('[data-testid=viewtoggle-list]');
    expect(button.innerHTML).toBe('List');

    act(() => {
        button.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });

    expect(container.textContent).toContain(fakeAsset.title);

    // remove the mock to ensure tests are completely isolated
    global.fetch.mockRestore();
});

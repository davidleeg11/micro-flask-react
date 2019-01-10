import React from 'react';
import { shallow } from 'enzyme';
import renderer from 'react-test-renderer';

import AddSite from '../AddSite';

test('AddSite renders properly', () => {
  const wrapper = shallow(<AddSite/>);
  const element = wrapper.find('form');
  expect(element.find('input').length).toBe(2);
  expect(element.find('input').get(0).props.name).toBe('site');
  expect(element.find('input').get(1).props.type).toBe('submit');
});

test('AddSite renders a snapshot properly', () => {
  const tree = renderer.create(<AddSite/>).toJSON();
  expect(tree).toMatchSnapshot();
});

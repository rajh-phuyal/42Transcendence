// all the helper functions are here

export const $id = (id) => document.getElementById(id) || null;

export const $class = (className) => document.getElementsByClassName(className) || [];

export const $tag = (tag) => document.getElementsByTagName(tag) || [];

export const $query = (query) => document.querySelector(query) || null;

export const $queryAll = (query) => document.querySelectorAll(query) || [];

export const $create = (element) => document.createElement(element) || null;

export const $append = (parent, child) => parent.appendChild(child) || null;

export const $remove = (element) => element.remove() || null;

export const $addClass = (element, className) => element.classList.add(className) || null;

export const $removeClass = (element, className) => element.classList.remove(className) || null;

export const $toggleClass = (element, className) => element.classList.toggle(className) || null;

export const $hasClass = (element, className) => element.classList.contains(className) || false;

export const $on = (element, event, callback) => element.addEventListener(event, callback) || null;

export const $off = (element, event, callback) => element.removeEventListener(event, callback) || null;

export const $emit = (element, event) => element.dispatchEvent(new Event(event)) || null;

export default {
    $id,
    $class,
    $tag,
    $query,
    $queryAll,
    $create,
    $append,
    $remove,
    $addClass,
    $removeClass,
    $toggleClass,
    $hasClass,
    $on,
    $off,
    $emit
};
/*
	Author: Andreas Älveborn
	URL: https://github.com/aelveborn/Wii-Scale

	This file is part of Wii-Scale
	Copyright (C) 2015 Andreas Älveborn

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License along
	with this program; if not, write to the Free Software Foundation, Inc.,
	51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

var loki = require('lokijs'),
	db = new loki('app-data.json');

var Entries = function(collection) {
	this.entries = collection;
};

Entries.prototype.add = function(entry) {
	this.entries.insert(entry);
};

Entries.prototype.get = function() {
	return this.entries.data;
};

Entries.prototype.remove = function(entry) {
	this.entries.remove(entry);
};

Entries.prototype.getUserEntries = function(user) {
	return this.entries.find({
		userName: { '$eq': user.name }
	});
};

Entries.prototype.removeUserEntries = function(user) {
	this.entries.removeWhere({
		userName: { '$eq': user.name }
	});
};

module.exports = Entries;
public fun MakeSegment(as_is _node, in _start, in _end, as_is _dim, in _array, optional _idx, in _rows_filled) {
  _nid=getnci(_node,"NID_NUMBER");
  if (!present(_idx)) {
    _idx=-1;
  }
  if (kind(_array) == 217) {
      write(*,_array);
      return(TreeShr->TreeMakeSegment(val(_nid),descr(_start),descr(_end),xd(_dim),xd(_array),val(_idx),val(_rows_filled)));
  } else {
      return(TreeShr->TreeMakeSegment(val(_nid),descr(_start),descr(_end),xd(_dim),descr(data(_array)),val(_idx),val(_rows_filled)));
  }
}

use pyo3::exceptions::PyValueError;
use pyo3::ffi;
use pyo3::prelude::*;
use pyo3::types::PyString;

#[pyfunction]
fn isplit(s: &Bound<'_, PyString>, sep: &Bound<'_, PyString>) -> PyResult<ISplit> {
    ISplit::new(s, sep)
}

#[pyfunction]
fn irsplit(s: &Bound<'_, PyString>, sep: &Bound<'_, PyString>) -> PyResult<IRSplit> {
    IRSplit::new(s, sep)
}

#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(isplit, m)?)?;
    m.add_function(wrap_pyfunction!(irsplit, m)?)?;
    m.add_class::<ISplit>()?;
    m.add_class::<IRSplit>()?;
    Ok(())
}

#[pyclass(module = "isplit")]
struct ISplit {
    s: Py<PyString>,
    sep: Py<PyString>,
    sep_len: ffi::Py_ssize_t,
    start: ffi::Py_ssize_t,
    end: ffi::Py_ssize_t,
    done: bool,
}

impl ISplit {
    fn new(s: &Bound<'_, PyString>, sep: &Bound<'_, PyString>) -> PyResult<Self> {
        let sep_len = unicode_len(sep)?;
        if sep_len == 0 {
            return Err(PyValueError::new_err("empty separator"));
        }
        let end = unicode_len(s)?;

        Ok(Self {
            s: s.clone().unbind(),
            sep: sep.clone().unbind(),
            sep_len,
            start: 0,
            end,
            done: false,
        })
    }
}

#[pymethods]
impl ISplit {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        if self.done {
            return Ok(None);
        }

        let result =
            if let Some(index) = unicode_find(py, &self.s, &self.sep, self.start, self.end, 1)? {
                let result = unicode_substring(py, &self.s, self.start, index)?;
                self.start = index + self.sep_len;
                result
            } else {
                let result = unicode_substring(py, &self.s, self.start, self.end)?;
                self.done = true;
                result
            };

        Ok(Some(result))
    }
}

#[pyclass(module = "isplit")]
struct IRSplit {
    s: Py<PyString>,
    sep: Py<PyString>,
    sep_len: ffi::Py_ssize_t,
    end: ffi::Py_ssize_t,
    done: bool,
}

impl IRSplit {
    fn new(s: &Bound<'_, PyString>, sep: &Bound<'_, PyString>) -> PyResult<Self> {
        let sep_len = unicode_len(sep)?;
        if sep_len == 0 {
            return Err(PyValueError::new_err("empty separator"));
        }
        let end = unicode_len(s)?;

        Ok(Self {
            s: s.clone().unbind(),
            sep: sep.clone().unbind(),
            sep_len,
            end,
            done: false,
        })
    }
}

#[pymethods]
impl IRSplit {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyAny>>> {
        if self.done {
            return Ok(None);
        }

        let result = if let Some(index) = unicode_find(py, &self.s, &self.sep, 0, self.end, -1)? {
            let result = unicode_substring(py, &self.s, index + self.sep_len, self.end)?;
            self.end = index;
            result
        } else {
            let result = unicode_substring(py, &self.s, 0, self.end)?;
            self.done = true;
            result
        };

        Ok(Some(result))
    }
}

fn unicode_len(s: &Bound<'_, PyString>) -> PyResult<ffi::Py_ssize_t> {
    let len = unsafe { ffi::PyUnicode_GetLength(s.as_ptr()) };
    if len < 0 {
        Err(PyErr::fetch(s.py()))
    } else {
        Ok(len)
    }
}

fn unicode_find(
    py: Python<'_>,
    s: &Py<PyString>,
    sep: &Py<PyString>,
    start: ffi::Py_ssize_t,
    end: ffi::Py_ssize_t,
    direction: i32,
) -> PyResult<Option<ffi::Py_ssize_t>> {
    let index = unsafe {
        ffi::PyUnicode_Find(
            s.as_ptr(),
            sep.as_ptr(),
            start,
            end,
            direction as std::ffi::c_int,
        )
    };

    if index == -2 {
        Err(PyErr::fetch(py))
    } else if index == -1 {
        Ok(None)
    } else {
        Ok(Some(index))
    }
}

fn unicode_substring(
    py: Python<'_>,
    s: &Py<PyString>,
    start: ffi::Py_ssize_t,
    end: ffi::Py_ssize_t,
) -> PyResult<Py<PyAny>> {
    let result = unsafe { ffi::PyUnicode_Substring(s.as_ptr(), start, end) };
    if result.is_null() {
        Err(PyErr::fetch(py))
    } else {
        Ok(unsafe { Py::from_owned_ptr(py, result) })
    }
}

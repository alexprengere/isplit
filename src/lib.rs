use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::pybacked::PyBackedStr;
use pyo3::types::PyString;

#[pyfunction]
fn isplit(s: PyBackedStr, sep: &str) -> PyResult<ISplit> {
    ISplit::new(s, sep)
}

#[pyfunction]
fn irsplit(s: PyBackedStr, sep: &str) -> PyResult<IRSplit> {
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
    s: PyBackedStr,
    sep: String,
    start: usize,
    done: bool,
}

impl ISplit {
    fn new(s: PyBackedStr, sep: &str) -> PyResult<Self> {
        if sep.is_empty() {
            return Err(PyValueError::new_err("empty separator"));
        }

        Ok(Self {
            s,
            sep: sep.to_owned(),
            start: 0,
            done: false,
        })
    }
}

#[pymethods]
impl ISplit {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(&mut self, py: Python<'_>) -> Option<Py<PyString>> {
        if self.done {
            return None;
        }

        let result = if let Some(index) = self.s[self.start..].find(&self.sep) {
            let index = self.start + index;
            let result = &self.s[self.start..index];
            self.start = index + self.sep.len();
            result
        } else {
            let result = &self.s[self.start..];
            self.done = true;
            result
        };

        Some(PyString::new(py, result).unbind())
    }
}

#[pyclass(module = "isplit")]
struct IRSplit {
    s: PyBackedStr,
    sep: String,
    end: usize,
    done: bool,
}

impl IRSplit {
    fn new(s: PyBackedStr, sep: &str) -> PyResult<Self> {
        if sep.is_empty() {
            return Err(PyValueError::new_err("empty separator"));
        }
        let end = s.len();

        Ok(Self {
            s,
            sep: sep.to_owned(),
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

    fn __next__(&mut self, py: Python<'_>) -> Option<Py<PyString>> {
        if self.done {
            return None;
        }

        let result = if let Some(index) = self.s[..self.end].rfind(&self.sep) {
            let result = &self.s[index + self.sep.len()..self.end];
            self.end = index;
            result
        } else {
            let result = &self.s[..self.end];
            self.done = true;
            result
        };

        Some(PyString::new(py, result).unbind())
    }
}

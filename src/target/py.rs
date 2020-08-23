use super::Target;
use std::{
    env::consts::EXE_SUFFIX,
    fs::{remove_file, write},
    io::{Error, ErrorKind, Result, Write},
	process::{Command, Stdio},
	mem,
};

pub struct Python {
	pub indentLevel: usize
}

impl Default for Python {
	fn default() -> Python {
		Python {
			indentLevel: 1
		}
	}
}

macro_rules! indent {
	($sel:ident) => (std::iter::repeat("    ").take($sel.indentLevel).collect::<String>())
}

impl Target for Python {
    fn get_name(&self) -> char {
        'p'
    }

    fn std(&self) -> String {
        String::from(include_str!("std/std.py"))
    }

    fn core_prelude(&self) -> String {
        String::from(include_str!("core/core.py"))
    }

    fn core_postlude(&self) -> String {
        String::new()
    }

    fn begin_entry_point(&self, global_scope_size: i32, memory_size: i32) -> String {
        format!(
			"def main():\n{}vm = machine_new({}, {})\n",
			indent!(self),
            global_scope_size,
            global_scope_size + memory_size,
        )
    }

    fn end_entry_point(&self) -> String {
        format!("\n{}machine_drop(vm)\n", indent!(self))
    }

    fn establish_stack_frame(&self, arg_size: i32, local_scope_size: i32) -> String {
        format!(
            "{}machine_establish_stack_frame(vm, {}, {})\n",
             indent!(self), arg_size, local_scope_size
        )
    }

    fn end_stack_frame(&self, return_size: i32, local_scope_size: i32) -> String {
        format!(
            "{}machine_end_stack_frame(vm, {}, {})\n",
            indent!(self), return_size, local_scope_size
        )
    }

    fn load_base_ptr(&self) -> String {
        format!("{}machine_load_base_ptr(vm)\n", indent!(self))
    }

    fn push(&self, n: f64) -> String {
        format!("{}machine_push(vm, {})\n", indent!(self), n)
    }

    fn add(&self) -> String {
        format!("{}machine_add(vm)\n", indent!(self))
    }

    fn subtract(&self) -> String {
        format!("{}machine_subtract(vm)\n", indent!(self))
    }

    fn multiply(&self) -> String {
        format!("{}machine_multiply(vm)\n", indent!(self))
    }

    fn divide(&self) -> String {
        format!("{}machine_divide(vm)\n", indent!(self))
    }

    fn sign(&self) -> String {
        format!("{}machine_sign(vm)\n", indent!(self))
    }

    fn allocate(&self) -> String {
        format!("{}machine_allocate(vm)\n", indent!(self))
    }

    fn free(&self) -> String {
        format!("{}machine_free(vm)\n", indent!(self))
    }

    fn store(&self, size: i32) -> String {
        format!("{}machine_store(vm, {})\n", indent!(self), size)
    }

    fn load(&self, size: i32) -> String {
        format!("{}machine_load(vm, {})\n", indent!(self), size)
    }

    fn fn_header(&self, name: String) -> String {
        String::new()
    }

    fn fn_definition(&self, name: String, body: String) -> String {
        format!("def {}(vm: Machine) -> None:\n{}\n", name, body)
    }

    fn call_fn(&self, name: String) -> String {
        format!("{}{}(vm)\n", indent!(self), name)
    }

    fn call_foreign_fn(&self, name: String) -> String {
        format!("{}{}(vm)\n", indent!(self), name)
    }

    fn begin_while(&mut self) -> String {
		let out = format!("{}while (machine_pop(vm)):\n", indent!(self));
		self.indentLevel += 1;
		out
    }

    fn end_while(&mut self) -> String {
		let out = format!("{}\n", indent!(self));
		self.indentLevel -= 1;
		out
    }

    fn compile(&self, code: String) -> Result<()> {
        if let Ok(_) = write("main.py", code) {
            return Result::Ok(());
        }
        Result::Err(Error::new(ErrorKind::Other, "error compiling "))
    }
}

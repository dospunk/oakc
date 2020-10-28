use super::Target;
use std::{
    env::consts::EXE_SUFFIX,
    fs::{remove_file, write},
    io::{Error, ErrorKind, Result, Write},
	process::{Command, Stdio},
	mem,
};

pub struct Python;

static mut indentLevel: usize = 1;

macro_rules! indent {
	() => (std::iter::repeat("    ").take(unsafe {indentLevel}).collect::<String>())
}

impl Target for Python {
    fn get_name(&self) -> char {
        'p'
    }

    fn is_standard(&self) -> bool {
        true
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
			indent!(),
            global_scope_size,
            global_scope_size + memory_size,
        )
    }

    fn end_entry_point(&self) -> String {
        format!("\n{}machine_drop(vm)\n\nif __name__ == \"__main__\":\n{}main()", indent!(), indent!())
    }

    fn establish_stack_frame(&self, arg_size: i32, local_scope_size: i32) -> String {
        format!(
            "{}machine_establish_stack_frame(vm, {}, {})\n",
             indent!(), arg_size, local_scope_size
        ) 
    }

    fn end_stack_frame(&self, return_size: i32, local_scope_size: i32) -> String {
        format!(
            "{}machine_end_stack_frame(vm, {}, {})\n",
            indent!(), return_size, local_scope_size
        )
    }

    fn load_base_ptr(&self) -> String {
        format!("{}machine_load_base_ptr(vm)\n", indent!())
    }

    fn push(&self, n: f64) -> String {
        format!("{}machine_push(vm, {})\n", indent!(), n)
    }

    fn add(&self) -> String {
        format!("{}machine_add(vm)\n", indent!())
    }

    fn subtract(&self) -> String {
        format!("{}machine_subtract(vm)\n", indent!())
    }

    fn multiply(&self) -> String {
        format!("{}machine_multiply(vm)\n", indent!())
    }

    fn divide(&self) -> String {
        format!("{}machine_divide(vm)\n", indent!())
    }

    fn sign(&self) -> String {
        format!("{}machine_sign(vm)\n", indent!())
    }

    fn allocate(&self) -> String {
        format!("{}machine_allocate(vm)\n", indent!())
    }

    fn free(&self) -> String {
        format!("{}machine_free(vm)\n", indent!())
    }

    fn store(&self, size: i32) -> String {
        format!("{}machine_store(vm, {})\n", indent!(), size)
    }

    fn load(&self, size: i32) -> String {
        format!("{}machine_load(vm, {})\n", indent!(), size)
    }

    fn fn_header(&self, name: String) -> String {
        String::new()
    }

    fn fn_definition(&self, name: String, body: String) -> String {
        format!("def {}(vm: Machine) -> None:\n{}\n", name, body)
    }

    fn call_fn(&self, name: String) -> String {
        format!("{}{}(vm)\n", indent!(), name)
    }

    fn call_foreign_fn(&self, name: String) -> String {
        format!("{}{}(vm)\n", indent!(), name)
    }

    fn begin_while(&self) -> String {
		let out = format!("{}while (machine_pop(vm)):\n", indent!());
		unsafe {indentLevel += 1;}
		out
    }

    fn end_while(&self) -> String {
		let out = format!("{}\n", indent!());
		unsafe {indentLevel -= 1;}
		out
    }

    fn compile(&self, code: String) -> Result<()> {
        if let Ok(_) = write("main.py", code) {
            return Result::Ok(());
        }
        Result::Err(Error::new(ErrorKind::Other, "error compiling "))
    }
}

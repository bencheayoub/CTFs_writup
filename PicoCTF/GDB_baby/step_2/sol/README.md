we open the file in ida and decompile it and we'll find this code:
```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  int i; // [rsp+18h] [rbp-8h]
  int v5; // [rsp+1Ch] [rbp-4h]

  v5 = 123098;
  for ( i = 0; i < 607; ++i )
    v5 += i;
  return v5;
}
```

so we can the code of the python directly
```python
v = 123098

i = 0
for i in range(607):
    v += i

print(v)
```
and we get the flag: academy{307019}

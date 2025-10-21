type MenuItem = {
  label: string
  icon?: string
  to?: string
  url?: string
  target?: string
  class?: string
  items?: MenuItem[]
  disabled?: boolean
  separator?: boolean
}

type MenuList = MenuItem[]
